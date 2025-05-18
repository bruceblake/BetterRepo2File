#!/usr/bin/env python3
"""
repo2file - Advanced CLI for repository consolidation
"""
import click
import sys
import os
import json
from pathlib import Path
from typing import Optional, List
import time
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
import requests

# Import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repo2file.dump import main as dump_standard
from repo2file.dump_smart import main as dump_smart
from repo2file.dump_token_aware import main as dump_token_aware
from repo2file.dump_ultra import main as dump_ultra

console = Console()

# API configuration
API_BASE_URL = os.environ.get('REPO2FILE_API', 'http://localhost:5000/api/v1')

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """repo2file - Advanced repository content consolidation for LLMs"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.option('--mode', type=click.Choice(['standard', 'smart', 'token', 'ultra']), 
              default='smart', help='Processing mode')
@click.option('--model', default='gpt-4', help='LLM model (for ultra mode: gpt-4, gpt-3.5-turbo, claude-3, llama, gemini-1.5-pro)')
@click.option('--budget', type=int, default=500000, help='Token budget')
@click.option('--profile', help='Use configuration profile')
@click.option('--exclude', multiple=True, help='Additional exclusion patterns')
@click.option('--file-types', multiple=True, help='File extensions to include')
@click.option('--preview', is_flag=True, help='Preview files before processing')
@click.option('--stats', is_flag=True, help='Show detailed statistics')
@click.option('--manifest', is_flag=True, help='Generate hierarchical manifest (for ultra mode)')
@click.option('--truncation', type=click.Choice(['semantic', 'basic', 'middle_summarize', 'business_logic']), 
              help='Truncation strategy (for ultra mode)')
def process(path, output, mode, model, budget, profile, exclude, file_types, preview, stats, manifest, truncation):
    """Process a repository or directory"""
    
    console.print(f"[bold blue]repo2file[/bold blue] - Processing {path}")
    console.print(f"Mode: [cyan]{mode}[/cyan]")
    
    if profile:
        console.print(f"Profile: [green]{profile}[/green]")
    
    start_time = time.time()
    
    # Build command based on mode
    if mode == 'ultra':
        cmd = [sys.executable, '-m', 'repo2file.dump_ultra', path, output]
        cmd.extend(['--model', model, '--budget', str(budget)])
        
        if manifest:
            cmd.append('--manifest')
        
        if truncation:
            cmd.extend(['--truncation', truncation])
        
        for pattern in exclude:
            cmd.extend(['--exclude', pattern])
    else:
        script_map = {
            'standard': 'repo2file.dump',
            'smart': 'repo2file.dump_smart',
            'token': 'repo2file.dump_token_aware'
        }
        
        cmd = [sys.executable, '-m', script_map[mode], path, output]
        
        # Add exclusion file
        gitignore_path = Path(path) / '.gitignore'
        if gitignore_path.exists():
            cmd.append(str(gitignore_path))
        
        if file_types:
            cmd.extend(file_types)
    
    # Show preview if requested
    if preview:
        show_preview(path, file_types)
        if not Confirm.ask("Continue with processing?"):
            return
    
    # Run processing with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Processing files...", total=None)
        
        import subprocess
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Monitor output
        while True:
            line = process.stdout.readline()
            if not line:
                break
            if "Processing:" in line:
                progress.update(task, description=line.strip())
        
        process.wait()
        
        if process.returncode != 0:
            console.print(f"[red]Error:[/red] {process.stderr.read()}")
            sys.exit(1)
    
    elapsed = time.time() - start_time
    console.print(f"\n[green]✓[/green] Processing complete in {elapsed:.1f}s")
    console.print(f"Output: [cyan]{output}[/cyan]")
    
    # Show statistics if requested
    if stats:
        show_statistics(output)

@cli.command()
@click.argument('repo_url')
@click.option('--mode', type=click.Choice(['standard', 'smart', 'token', 'ultra']), 
              default='smart', help='Processing mode')
@click.option('--model', default='gpt-4', help='LLM model (for ultra mode: gpt-4, gpt-3.5-turbo, claude-3, llama, gemini-1.5-pro)')
@click.option('--budget', type=int, default=500000, help='Token budget')
@click.option('--output', help='Output file (default: repo_name.txt)')
def github(repo_url, mode, model, budget, output):
    """Process a GitHub repository"""
    
    console.print(f"[bold blue]repo2file[/bold blue] - Processing GitHub repository")
    console.print(f"Repository: [cyan]{repo_url}[/cyan]")
    console.print(f"Mode: [cyan]{mode}[/cyan]")
    
    if not output:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        output = f"{repo_name}.txt"
    
    # Call API
    with console.status("Processing repository..."):
        response = requests.post(f'{API_BASE_URL}/process', json={
            'mode': mode,
            'github_url': repo_url,
            'options': {
                'model': model,
                'token_budget': budget
            }
        })
    
    if response.status_code == 200:
        data = response.json()
        
        # Save output
        with open(output, 'w') as f:
            f.write(data['content'])
        
        console.print(f"\n[green]✓[/green] Processing complete")
        console.print(f"Output: [cyan]{output}[/cyan]")
        
        # Show stats
        stats = data.get('stats', {})
        if stats:
            table = Table(title="Processing Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Processing Time", f"{stats.get('processing_time', 0):.1f}s")
            table.add_row("Output Size", f"{stats.get('output_size', 0):,} bytes")
            table.add_row("Mode", mode)
            
            console.print(table)
    else:
        error = response.json().get('error', 'Unknown error')
        console.print(f"[red]Error:[/red] {error}")
        sys.exit(1)

@cli.command()
def profiles():
    """List available configuration profiles"""
    
    console.print("[bold]Available Profiles[/bold]\n")
    
    response = requests.get(f'{API_BASE_URL}/../profiles/')
    if response.status_code == 200:
        profiles_data = response.json()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Profile", style="cyan", width=15)
        table.add_column("Description", style="white", width=40)
        table.add_column("Mode", style="green", width=10)
        
        for profile in profiles_data:
            table.add_row(
                profile['name'],
                profile['description'],
                profile['mode']
            )
        
        console.print(table)
    else:
        console.print("[red]Error loading profiles[/red]")

@cli.command()
@click.argument('profile_name')
def profile(profile_name):
    """Show details of a specific profile"""
    
    response = requests.get(f'{API_BASE_URL}/../profiles/{profile_name}')
    if response.status_code == 200:
        data = response.json()
        
        # Create a formatted panel
        content = f"""[bold cyan]Profile:[/bold cyan] {data['name']}
[bold]Description:[/bold] {data.get('description', 'N/A')}
[bold]Mode:[/bold] {data.get('mode', 'smart')}
[bold]Model:[/bold] {data.get('model', 'gpt-4')}
[bold]Token Budget:[/bold] {data.get('token_budget', 500000):,}

[bold]File Extensions:[/bold]
{', '.join(data.get('file_extensions', [])) or 'All files'}

[bold]Exclude Patterns:[/bold]
{chr(10).join(data.get('exclude_patterns', [])) or 'None'}

[bold]Priority Patterns:[/bold]"""
        
        for pattern, priority in data.get('priority_patterns', {}).items():
            content += f"\n  {pattern}: {priority}"
        
        panel = Panel(content, title=f"Profile: {profile_name}", border_style="green")
        console.print(panel)
    else:
        console.print(f"[red]Profile '{profile_name}' not found[/red]")

@cli.command()
def modes():
    """List available processing modes"""
    
    console.print("[bold]Processing Modes[/bold]\n")
    
    response = requests.get(f'{API_BASE_URL}/modes')
    if response.status_code == 200:
        modes_data = response.json()
        
        for mode_name, mode_info in modes_data.items():
            console.print(f"[bold cyan]{mode_name}[/bold cyan] - {mode_info['name']}")
            console.print(f"  {mode_info['description']}")
            console.print(f"  Features:")
            for feature in mode_info['features']:
                console.print(f"    • {feature}")
            console.print()
    else:
        console.print("[red]Error loading modes[/red]")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--lines', type=int, default=50, help='Number of lines to show')
@click.option('--syntax', is_flag=True, help='Show with syntax highlighting')
def preview_file(file_path, lines, syntax):
    """Preview a file's content"""
    
    console.print(f"[bold]Preview:[/bold] {file_path}\n")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if syntax:
        # Determine language from extension
        ext = Path(file_path).suffix.lstrip('.')
        lang_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'go': 'go',
            'rs': 'rust',
            'rb': 'ruby',
            'php': 'php',
        }
        language = lang_map.get(ext, 'text')
        
        syntax_obj = Syntax(content[:lines*80], language, theme="monokai", line_numbers=True)
        console.print(syntax_obj)
    else:
        lines_list = content.splitlines()[:lines]
        for i, line in enumerate(lines_list, 1):
            console.print(f"{i:4d} | {line}")

@cli.command()
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def config():
    """Show current configuration"""
    
    config_data = {
        'api_url': API_BASE_URL,
        'cache_dir': str(Path.home() / '.repo2file' / 'cache'),
        'profiles_dir': str(Path.home() / '.repo2file' / 'profiles'),
        'default_mode': 'smart',
        'default_model': 'gpt-4',
        'default_budget': 500000,
    }
    
    if output_json:
        console.print(json.dumps(config_data, indent=2))
    else:
        table = Table(title="repo2file Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in config_data.items():
            table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(table)

@cli.command()
def interactive():
    """Interactive mode with prompts"""
    
    console.print("[bold blue]repo2file Interactive Mode[/bold blue]\n")
    
    # Get path
    path = Prompt.ask("Enter repository/directory path")
    if not Path(path).exists():
        console.print(f"[red]Error:[/red] Path '{path}' does not exist")
        return
    
    # Get mode
    mode = Prompt.ask(
        "Select processing mode",
        choices=['standard', 'smart', 'token', 'ultra'],
        default='smart'
    )
    
    # Get output file
    default_output = f"{Path(path).name}_output.txt"
    output = Prompt.ask("Output file", default=default_output)
    
    # Mode-specific options
    options = {}
    if mode == 'ultra':
        model = Prompt.ask("LLM Model", choices=['gpt-4', 'gpt-3.5-turbo', 'claude-3'], default='gpt-4')
        budget = Prompt.ask("Token Budget", default="500000")
        options = {'model': model, 'budget': int(budget)}
    
    # Confirm
    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Path: {path}")
    console.print(f"  Mode: {mode}")
    console.print(f"  Output: {output}")
    for key, value in options.items():
        console.print(f"  {key.title()}: {value}")
    
    if Confirm.ask("\nProceed with processing?"):
        # Run processing
        cmd = ['process', path, output, '--mode', mode]
        for key, value in options.items():
            cmd.extend([f'--{key}', str(value)])
        
        # Import click context and invoke
        ctx = click.Context(cli)
        cli.invoke(ctx, cmd)

# Helper functions
def show_preview(path: Path, file_types: List[str]):
    """Show preview of files to be processed"""
    
    console.print("\n[bold]Files to be processed:[/bold]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan", width=50)
    table.add_column("Size", style="green", width=10)
    table.add_column("Type", style="yellow", width=10)
    
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files[:10]:  # Show first 10 files
            if file_types and not any(file.endswith(ext) for ext in file_types):
                continue
            
            file_path = Path(root) / file
            rel_path = file_path.relative_to(path)
            size = file_path.stat().st_size
            ext = file_path.suffix
            
            table.add_row(
                str(rel_path),
                f"{size:,} B",
                ext or "N/A"
            )
            count += 1
            
            if count >= 10:
                break
        if count >= 10:
            break
    
    console.print(table)
    console.print(f"\n... and more files")

def show_statistics(output_file: Path):
    """Show statistics about the output file"""
    
    if not Path(output_file).exists():
        return
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse statistics from the output
    lines = content.splitlines()
    stats = {}
    
    for line in lines[-20:]:  # Check last 20 lines for stats
        if 'Files Processed:' in line:
            stats['files_processed'] = line.split(':')[1].strip()
        elif 'Token Usage:' in line:
            stats['token_usage'] = line.split(':')[1].strip()
        elif 'Processing Time:' in line:
            stats['processing_time'] = line.split(':')[1].strip()
    
    if stats:
        table = Table(title="Processing Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            table.add_row(key.replace('_', ' ').title(), value)
        
        console.print(table)

if __name__ == '__main__':
    cli()