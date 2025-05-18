"""
Docker Compose file parser for extracting service configurations
"""
import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class ServiceConfig:
    """Configuration for a single Docker service"""
    name: str
    build_context: Optional[str] = None
    image: Optional[str] = None
    volumes: List[str] = None
    command: Optional[str] = None
    test_command: Optional[str] = None
    environment: Dict[str, str] = None
    depends_on: List[str] = None
    ports: List[str] = None
    
    def __post_init__(self):
        if self.volumes is None:
            self.volumes = []
        if self.environment is None:
            self.environment = {}
        if self.depends_on is None:
            self.depends_on = []
        if self.ports is None:
            self.ports = []

@dataclass
class ComposeConfig:
    """Parsed Docker Compose configuration"""
    version: str
    services: Dict[str, ServiceConfig]
    networks: List[str]
    volumes: List[str]
    compose_file_path: Path
    
    def get_compose_network(self) -> str:
        """Get the default network name for this compose project"""
        # Docker Compose creates a default network named <project>_default
        project_name = self.compose_file_path.parent.name
        return f"{project_name}_default"
    
    def get_skip_services(self) -> List[str]:
        """Get services that should be skipped during analysis"""
        # Skip database and cache services by default
        skip_patterns = ['db', 'database', 'mysql', 'postgres', 'redis', 'cache']
        return [name for name in self.services 
                if any(pattern in name.lower() for pattern in skip_patterns)]

class ComposeParser:
    """Parse Docker Compose files and extract service configurations"""
    
    # Default test commands for common frameworks
    DEFAULT_TEST_COMMANDS = {
        'python': 'pytest -q --json-report',
        'node': 'npm test',
        'ruby': 'bundle exec rspec',
        'java': 'mvn test',
        'go': 'go test ./...',
    }
    
    def __init__(self, compose_file: Path):
        self.compose_file = compose_file
        self.base_dir = compose_file.parent
        
    def parse(self) -> ComposeConfig:
        """Parse the compose file and return configuration"""
        with open(self.compose_file, 'r') as f:
            data = yaml.safe_load(f)
        
        version = str(data.get('version', '3'))
        services = self._parse_services(data.get('services', {}))
        networks = list(data.get('networks', {}).keys())
        volumes = list(data.get('volumes', {}).keys())
        
        return ComposeConfig(
            version=version,
            services=services,
            networks=networks,
            volumes=volumes,
            compose_file_path=self.compose_file
        )
    
    def _parse_services(self, services_data: Dict[str, Any]) -> Dict[str, ServiceConfig]:
        """Parse individual service configurations"""
        services = {}
        
        for name, config in services_data.items():
            service = ServiceConfig(name=name)
            
            # Extract build context
            if 'build' in config:
                if isinstance(config['build'], str):
                    service.build_context = config['build']
                elif isinstance(config['build'], dict):
                    service.build_context = config['build'].get('context', '.')
            
            # Extract other fields
            service.image = config.get('image')
            service.command = config.get('command')
            service.environment = self._parse_environment(config.get('environment', {}))
            service.depends_on = config.get('depends_on', [])
            service.ports = config.get('ports', [])
            
            # Parse volumes
            service.volumes = self._parse_volumes(config.get('volumes', []))
            
            # Infer test command
            service.test_command = self._infer_test_command(service)
            
            services[name] = service
        
        return services
    
    def _parse_environment(self, env_data: Any) -> Dict[str, str]:
        """Parse environment variables from various formats"""
        if isinstance(env_data, dict):
            return {k: str(v) for k, v in env_data.items()}
        elif isinstance(env_data, list):
            env_dict = {}
            for item in env_data:
                if '=' in item:
                    key, value = item.split('=', 1)
                    env_dict[key] = value
            return env_dict
        return {}
    
    def _parse_volumes(self, volumes_data: List[Any]) -> List[str]:
        """Parse volume mappings"""
        volumes = []
        for volume in volumes_data:
            if isinstance(volume, str):
                volumes.append(volume)
            elif isinstance(volume, dict):
                # Handle long form volume syntax
                source = volume.get('source', '')
                target = volume.get('target', '') 
                if source and target:
                    volumes.append(f"{source}:{target}")
        return volumes
    
    def _infer_test_command(self, service: ServiceConfig) -> Optional[str]:
        """Infer the test command based on the service configuration"""
        # Check if there's a custom test command in the environment
        if 'TEST_COMMAND' in service.environment:
            return service.environment['TEST_COMMAND']
        
        # Check build context for language hints
        if service.build_context:
            context_path = self.base_dir / service.build_context
            if context_path.exists():
                # Look for language-specific files
                if (context_path / 'package.json').exists():
                    return self.DEFAULT_TEST_COMMANDS['node']
                elif (context_path / 'requirements.txt').exists() or \
                     (context_path / 'setup.py').exists():
                    return self.DEFAULT_TEST_COMMANDS['python']
                elif (context_path / 'Gemfile').exists():
                    return self.DEFAULT_TEST_COMMANDS['ruby']
                elif (context_path / 'pom.xml').exists():
                    return self.DEFAULT_TEST_COMMANDS['java']
                elif (context_path / 'go.mod').exists():
                    return self.DEFAULT_TEST_COMMANDS['go']
        
        return None

def load_project_config(project_root: Path) -> Optional[Dict[str, Any]]:
    """Load repo2file.yml configuration if it exists"""
    config_path = project_root / 'repo2file.yml'
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return None