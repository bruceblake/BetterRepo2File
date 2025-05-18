==================================================
SECTION 1: FOR AI PLANNING AGENT (e.g., Gemini 1.5 Pro in AI Studio)
Copy and paste this section into your Planning AI.
==================================================

MY VIBE / PRIMARY GOAL:
Create a modern web application with great performance

PROJECT SNAPSHOT & HIGH-LEVEL CONTEXT:
- Primary Language: python
- Key Frameworks/Libraries: Python
- Core Modules/Areas:

This initial context provides a strategic overview. More detailed code will be supplied to the coding agent based on your plan.



==================================================
SECTION 2: FOR AI CODING AGENT (e.g., Local Claude Code)
This section contains the detailed codebase context and the plan from the AI Planning Agent.
==================================================

PLAN/INSTRUCTIONS FROM AI PLANNING AGENT (Gemini 1.5 Pro):
SECTION 1: FOR AI PLANNING AGENT (e.g., Gemini 1.5 Pro in AI Studio)
Copy and paste this section into your Planning AI.
==================================================

Project Structure Summary:
- /app
  - app.py (Flask application)
  - /static
  - /templates

Key Technologies:
- Python Flask
- JavaScript
- CSS

[[FILE_START: app/app.py]]
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"
[[FILE_END]]

==================================================

--- DETAILED CODEBASE CONTEXT ---




## Processing Notes
- Files are processed by importance score
- Content is intelligently truncated to fit token budget
- Binary and auto-generated files are excluded
- Lock files are summarized

## Directory Structure
```
/
    ├── .claude/
    │   └── settings.local.json
    ├── .git/
    │   ├── hooks/
    │   │   ├── applypatch-msg.sample
    │   │   ├── commit-msg.sample
    │   │   ├── fsmonitor-watchman.sample
    │   │   ├── post-update.sample
    │   │   ├── pre-applypatch.sample
    │   │   ├── pre-commit.sample
    │   │   ├── pre-merge-commit.sample
    │   │   ├── pre-push.sample
    │   │   ├── pre-rebase.sample
    │   │   ├── pre-receive.sample
    │   │   ├── prepare-commit-msg.sample
    │   │   ├── push-to-checkout.sample
    │   │   ├── sendemail-validate.sample
    │   │   └── update.sample
    │   ├── info/
    │   │   └── exclude
    │   ├── logs/
    │   ├── objects/
    │   │   ├── 0d/
    │   │   │   └── 0c62667a067f0d89611a4684b89be88b91609e
    │   │   ├── 13/
    │   │   │   └── 24bc6b605e48466c5744097be1fe5345651061
    │   │   ├── 15/
    │   │   │   └── 898d838a481f63fa5ab37c1242b1c744f201e1
    │   │   ├── 1c/
    │   │   │   └── e54fc2fc8d798db4959cc7ad8cd16f0ad5122b
    │   │   ├── 2d/
    │   │   │   └── f68f22f44856de7132c74b81a5cd38e60d5a4a
    │   │   ├── 30/
    │   │   │   └── 683c2fbe391cfe58f09378e6918fcb1f573b30
    │   │   ├── 32/
    │   │   │   └── 68b4c851ff31fc4b0b5634ecd8151286ba9d30
    │   │   ├── 34/
    │   │   │   └── 6bff6e8ffabdd3506ad5f24b619d3787224feb
    │   │   ├── 35/
    │   │   │   └── 629f9554f2394aa95e37325d0451ecd9b8abb2
    │   │   ├── 37/
    │   │   │   └── 61ce9c07afff5c77cee476fbd01dbbe2e40529
    │   │   ├── 47/
    │   │   │   └── 5035d6f821b18b1352f59ac5496ee5cf2d1cc8
    │   │   ├── 48/
    │   │   │   └── 90233a4d9a92774a14a44f64731c6cae9f1d12
    │   │   ├── 49/
    │   │   │   ├── 0ef67b8a7476e62431f95de3636dcb21f66f22
    │   │   │   └── 96b8385705c79d197dbb3ef96dc7e716976786
    │   │   ├── 4b/
    │   │   │   └── a3e4c2dc4c326b4cf6d9260b12d9c8d1088e35
    │   │   ├── 53/
    │   │   │   └── 1d316c61d808ced22f2f3aa3cd7a0be17f50d7
    │   │   ├── 56/
    │   │   │   └── 426b89689759ced8f6fd3a2a4b6a47689de44b
    │   │   ├── 5a/
    │   │   │   └── cf850b9c11ebcec2e50490c190219b8a1478ee
    │   │   ├── 60/
    │   │   │   └── bf4661c81275b935f32a72b5781e94c204abd0
    │   │   ├── 64/
    │   │   │   └── 841079656b96fdc7d80b5e1f59f6ea1b4ae117
    │   │   ├── 67/
    │   │   │   └── 2112dbc925dbee57a009818bfda7da957d858d
    │   ├── refs/
    │   │   ├── heads/
    │   │   │   └── main
    │   │   ├── remotes/
    │   │   │   └── origin/
    │   │   │       └── main
    │   │   └── tags/
    │   ├── COMMIT_EDITMSG
    │   ├── config
    │   ├── description
    │   ├── HEAD
    │   └── index
    ├── app/
    │   ├── __pycache__/
    │   ├── static/
    │   │   ├── css/
    │   │   │   └── styles.css
    │   │   └── js/
    │   │       └── script.js
    │   ├── templates/
    │   │   └── index.html
    │   ├── api.py
    │   ├── app.py
    │   └── profiles.py
    ├── docs/
    │   └── GEMINI_FEATURES.md
    ├── repo2file/
    │   ├── __pycache__/
    │   ├── .gitignore
    │   ├── action_blocks.py
    │   ├── cli.py
    │   ├── code_analyzer.py
    │   ├── dump.py
    │   ├── dump_smart.py
    │   ├── dump_token_aware.py
```


File Contents:
==================================================


[[FILE_START: app/app.py]]
File: app/app.py
Language: python
Size: 12,233 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/action_blocks.py]]
File: repo2file/action_blocks.py
Language: python
Size: 13,054 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/token_manager.py]]
File: repo2file/token_manager.py
Language: python
Size: 6,178 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: app/profiles.py]]
File: app/profiles.py
Language: python
Size: 10,094 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/llm_augmenter.py]]
File: repo2file/llm_augmenter.py
Language: python
Size: 12,367 bytes | Tokens: 50
----------------------------------------
[Error reading file: TodoItem.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: repo2file/cli.py]]
File: repo2file/cli.py
Language: python
Size: 15,560 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/git_analyzer.py]]
File: repo2file/git_analyzer.py
Language: python
Size: 16,797 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/code_analyzer.py]]
File: repo2file/code_analyzer.py
Language: python
Size: 17,318 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/dump_smart.py]]
File: repo2file/dump_smart.py
Language: python
Size: 21,988 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/dump_token_aware.py]]
File: repo2file/dump_token_aware.py
Language: python
Size: 35,579 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/dump_ultra.py]]
File: repo2file/dump_ultra.py
Language: python
Size: 100,568 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: .git/HEAD]]
File: .git/HEAD
Language: Unknown
Size: 21 bytes | Tokens: 7
----------------------------------------
ref: refs/heads/main



[[FILE_START: .git/refs/heads/main]]
File: .git/refs/heads/main
Language: Unknown
Size: 41 bytes | Tokens: 25
----------------------------------------
64841079656b96fdc7d80b5e1f59f6ea1b4ae117



[[FILE_START: .git/refs/remotes/origin/main]]
File: .git/refs/remotes/origin/main
Language: Unknown
Size: 41 bytes | Tokens: 26
----------------------------------------
531d316c61d808ced22f2f3aa3cd7a0be17f50d7



[[FILE_START: .git/objects/49/0ef67b8a7476e62431f95de3636dcb21f66f22]]
File: .git/objects/49/0ef67b8a7476e62431f95de3636dcb21f66f22
Language: Unknown
Size: 53 bytes | Tokens: 24
----------------------------------------
x+)JMU06g040031Q(N.,(*fl;kRbue 8q{


[[FILE_START: .git/objects/cf/f3c1b5bfebc11af56a121e655e33e3d807376e]]
File: .git/objects/cf/f3c1b5bfebc11af56a121e655e33e3d807376e
Language: Unknown
Size: 54 bytes | Tokens: 27
----------------------------------------
x+)JMU06g040031Q(N.,(*ft]kX3
e)< Z


[[FILE_START: .git/objects/86/773597935aaf215b24fc3b424c638449192757]]
File: .git/objects/86/773597935aaf215b24fc3b424c638449192757
Language: Unknown
Size: 54 bytes | Tokens: 26
----------------------------------------
x+)JMU06g040031Q(N.,(*fֹ:$<1By¦n T


[[FILE_START: .git/objects/1c/e54fc2fc8d798db4959cc7ad8cd16f0ad5122b]]
File: .git/objects/1c/e54fc2fc8d798db4959cc7ad8cd16f0ad5122b
Language: Unknown
Size: 55 bytes | Tokens: 28
----------------------------------------
x+)JMU0`040031QKI(aX/2kcJmRL]۴ Oc


[[FILE_START: .git/objects/a9/575e74353b292a5ab7dcf16d0e2871ac54731f]]
File: .git/objects/a9/575e74353b292a5ab7dcf16d0e2871ac54731f
Language: Unknown
Size: 55 bytes | Tokens: 28
----------------------------------------
x+)JMU0`040031Q(.I-K..f8il'2J8Tk o


[[FILE_START: .git/objects/8b/f5fcb31c4b5651caa9fbe60fc290f2d0e57007]]
File: .git/objects/8b/f5fcb31c4b5651caa9fbe60fc290f2d0e57007
Language: Unknown
Size: 55 bytes | Tokens: 24
----------------------------------------
x+)JMU0`040031QKI(a0k倬皷+ q


[[FILE_START: .git/objects/0d/0c62667a067f0d89611a4684b89be88b91609e]]
File: .git/objects/0d/0c62667a067f0d89611a4684b89be88b91609e
Language: Unknown
Size: 55 bytes | Tokens: 27
----------------------------------------
x+)JMU0`040031Q(.I-K..f^lo7ոng
 l


[[FILE_START: .git/objects/a8/48eb18cb332cebe54491a34b56e05154d965cc]]
File: .git/objects/a8/48eb18cb332cebe54491a34b56e05154d965cc
Language: Unknown
Size: 70 bytes | Tokens: 32
----------------------------------------
x+)JMU0d01 b^*zD)_tOL*fVURLgӊ 9


[[FILE_START: .git/objects/35/629f9554f2394aa95e37325d0451ecd9b8abb2]]
File: .git/objects/35/629f9554f2394aa95e37325d0451ecd9b8abb2
Language: Unknown
Size: 70 bytes | Tokens: 41
----------------------------------------
x+)JMU0d01 bq%֚ZQ|(\R,*fh+7>9jbk'OIp ٲ7


[[FILE_START: .git/objects/b6/2a8fec1703cf8c73727d8064c1b85167c9f4c4]]
File: .git/objects/b6/2a8fec1703cf8c73727d8064c1b85167c9f4c4
Language: Unknown
Size: 71 bytes | Tokens: 38
----------------------------------------
x+)JMU0d01 b^*zD)_tOL*f8J}K3~|< F


[[FILE_START: .git/description]]
File: .git/description
Language: Unknown
Size: 73 bytes | Tokens: 14
----------------------------------------
Unnamed repository; edit this file 'description' to name the repository.



[[FILE_START: .git/objects/e6/e4afae3ae82e804721c861308f8e634c5ab187]]
File: .git/objects/e6/e4afae3ae82e804721c861308f8e634c5ab187
Language: Unknown
Size: 111 bytes | Tokens: 56
----------------------------------------
x%A Fas
ObWsZҀ}ys.]9$bGzX=QmzY6n='jU]D؂o`}<)°7$L


[[FILE_START: requirements.txt]]
File: requirements.txt
Language: Unknown
Size: 113 bytes | Tokens: 50
----------------------------------------
[Error reading file: GitInsight.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/objects/53/1d316c61d808ced22f2f3aa3cd7a0be17f50d7]]
File: .git/objects/53/1d316c61d808ced22f2f3aa3cd7a0be17f50d7
Language: Unknown
Size: 177 bytes | Tokens: 84
----------------------------------------
xM0]swIBc\qLBRPo/|s&Q)&EZQ j֕dYv`SѢ*)!3L@"s867"PRUu#=m"[3uv&肕ʫI=M6E&:n=hfYLӘ}&Tz


[[FILE_START: .git/objects/a0/bb05c7fa068f5d06db4b6524ab980d9c1dfe36]]
File: .git/objects/a0/bb05c7fa068f5d06db4b6524ab980d9c1dfe36
Language: Unknown
Size: 177 bytes | Tokens: 73
----------------------------------------
x+)JMU047c040031QH,+d:=GCOY&8K\EH	[W.vzCUev6wy'\#'Ƈ&@P\X`4j'KqF,onX	$5 '$A?[9b>U!m `K


[[FILE_START: .git/objects/c3/e52d5b4a93af420a4010aec8896a9a6d6242ad]]
File: .git/objects/c3/e52d5b4a93af420a4010aec8896a9a6d6242ad
Language: Unknown
Size: 178 bytes | Tokens: 87
----------------------------------------
x+)JMU047c040031QH,+dإya;c,]<Ka
\EHŉeC>K'oID#̜bi*fUe^q_xUo':61 ĒdmZoę6~܂Ēb6xZ	.<-` 
M


[[FILE_START: .git/objects/67/2112dbc925dbee57a009818bfda7da957d858d]]
File: .git/objects/67/2112dbc925dbee57a009818bfda7da957d858d
Language: Unknown
Size: 178 bytes | Tokens: 74
----------------------------------------
x+)JMU047c040031QH,+dإya;c,]<Ka
\EH	[W.vzCUeMW1(
Ƌrx;($d&3x-qXSL=QP[XZ П-S_s1몐6 یM


[[FILE_START: .git/objects/2d/f68f22f44856de7132c74b81a5cd38e60d5a4a]]
File: .git/objects/2d/f68f22f44856de7132c74b81a5cd38e60d5a4a
Language: Unknown
Size: 178 bytes | Tokens: 97
----------------------------------------
x+)JMU047c040031QH,+dإya;c,]<Ka
\EHκL	?<ж-?zdB^?TEAQ~ZfNj1Hٴ{*2o`x*O BqIbIf267{jRL?DAIjnANbIj1C?eOЄO :M


[[FILE_START: .git/hooks/post-update.sample]]
File: .git/hooks/post-update.sample
Language: Unknown
Size: 189 bytes | Tokens: 44
----------------------------------------
#!/bin/sh
#
# An example hook script to prepare a packed repository for use over
# dumb transports.
#
# To enable this hook, rename this file to "post-update".

exec git update-server-info



[[FILE_START: .git/info/exclude]]
File: .git/info/exclude
Language: Unknown
Size: 240 bytes | Tokens: 63
----------------------------------------
# git ls-files --others --exclude-from=.git/info/exclude
# Lines that start with '#' are comments.
# For a project mostly in C, the following would be a good set of
# exclude patterns (uncomment them if you want to use them):
# *.[oa]
# *~



[[FILE_START: .git/objects/db/0415249d19e01a71b95e60905fdb389c46540e]]
File: .git/objects/db/0415249d19e01a71b95e60905fdb389c46540e
Language: Unknown
Size: 256 bytes | Tokens: 122
----------------------------------------
x+)JMU025c040031QK,L/Jeبqyg׽o*gPWss)?ݏjB:9ewfL<w_+-,OM@!A[{Fǽx-J-7JIe>n66wo	[ʯFjMQjaifQjnj^I^IE	ó'YkpW<hߗT4O8!:6c6ٻjl</ kq


[[FILE_START: .git/objects/fa/99c12e6116e0b29bbee2140e04e8e67254fcea]]
File: .git/objects/fa/99c12e6116e0b29bbee2140e04e8e67254fcea
Language: Unknown
Size: 256 bytes | Tokens: 110
----------------------------------------
x+)JMU025c040031QK,L/Jeبqyg׽o*gPWss)?ݏjB:9ewfL<w_+-,OM@!!]QIp6v]~kjmk/D( (-3'sps%kw=\lzzԚ̢ԼbgO֯zx"Ѡ/'jc;PBQi^q{:	 Rl 


[[FILE_START: .git/objects/b0/1eed7b15aeb654a42dea737e0689409c01cec7]]
File: .git/objects/b0/1eed7b15aeb654a42dea737e0689409c01cec7
Language: Unknown
Size: 256 bytes | Tokens: 121
----------------------------------------
x+)JMU025c040031QK,L/Jeبqyg׽o*gPW#r8~]^wU~ WG_0Όn|k1($0,z[,mT3x3e2l~9-!O<KgA)J-,,JM+)+(axd:z
'
}6՚*g0^[8묣yOʜ  '%iH


[[FILE_START: .git/objects/30/683c2fbe391cfe58f09378e6918fcb1f573b30]]
File: .git/objects/30/683c2fbe391cfe58f09378e6918fcb1f573b30
Language: Unknown
Size: 256 bytes | Tokens: 114
----------------------------------------
x+)JMU025c040031QK,L/Jeبqyg׽o*gPWss)?ݏjB:9ewfL<w_+-,OM@!Sh띸֝̚"[Zop\azvDjB)J-,,JM+)+(axd:z
'
}6՚*g0^[8묣yOʜ  jh


[[FILE_START: .git/config]]
File: .git/config
Language: Unknown
Size: 270 bytes | Tokens: 84
----------------------------------------
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
[remote "origin"]
	url = https://github.com/bruceblake/BetterRepo2File.git
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
	remote = origin
	merge = refs/heads/main



[[FILE_START: .git/COMMIT_EDITMSG]]
File: .git/COMMIT_EDITMSG
Language: Unknown
Size: 271 bytes | Tokens: 50
----------------------------------------
Fix empty model parameter issue with Gemini profile

- Reorder argument processing to handle profile first
- Only override model if explicitly provided and non-empty
- Add debug logging to trace model setting
- Fix command building to avoid sending empty model parameter



[[FILE_START: .git/objects/64/841079656b96fdc7d80b5e1f59f6ea1b4ae117]]
File: .git/objects/64/841079656b96fdc7d80b5e1f59f6ea1b4ae117
Language: Unknown
Size: 303 bytes | Tokens: 155
----------------------------------------
xPN0fSr'v$`
$6FǾ''rҾ=lLl)* z((d5rp6{1nrc+N
1m+謵VM'SVN)W2x!GJiB
Q1]0,
!9˹u
E%<V>1e"-2gq])PLt
0Q^>B:c^Hed01gp ml}q>dcsV,a'GywWs"+


[[FILE_START: .git/objects/49/96b8385705c79d197dbb3ef96dc7e716976786]]
File: .git/objects/49/96b8385705c79d197dbb3ef96dc7e716976786
Language: Unknown
Size: 314 bytes | Tokens: 150
----------------------------------------
x+)JMU063d040031QK,L/Jeheo!ּt&CU:0|7/sR_Jgg*J+dVٓY_k@"LE~Jj|b^bNeUjHm~B;M?kmreڔ<7خ$;6G&el97wɛBm +,N͋O,O,J)yX܂8P=Y#+/))J),p8z:S}
WU12t"˺f\}?sσVe 2Z3


[[FILE_START: .git/objects/f9/83e18803e087036e466ae23103f94dd00ca59a]]
File: .git/objects/f9/83e18803e087036e466ae23103f94dd00ca59a
Language: Unknown
Size: 314 bytes | Tokens: 140
----------------------------------------
x+)JMU063d040031QK,L/Jeheo!ּt&CU:0|7/sR_Jgg*J+dȎ+[w~9U낮uN	SSYZR-PNZE[+bY}64 <
+:ͭ>?cd$%ŹE% F[N7f憨Pۮ
KSRA?hy< !!-`O{KsJA
/-'@B(ꇈ-ox@;: 5P


[[FILE_START: .git/objects/d9/ce831515c31e73c52e3e4fde1e40147ca4736d]]
File: .git/objects/d9/ce831515c31e73c52e3e4fde1e40147ca4736d
Language: Unknown
Size: 314 bytes | Tokens: 153
----------------------------------------
x+)JMU063d040031QK,L/Jeheo!ּt&CU:0|7/sR_Jgg*J+dVٓY_k@"LE~Jj|b^bNeUjHm~B;M?kmreڔ<7خ$;6G&el97wɛBm +,N͋O,O,J)yX܂8P=Y#+/))J)l|[KMꛧljL?'U12t"˺f\}?sσVe 7


[[FILE_START: .git/objects/7b/c736963d6dacd9f6e3fbdc56a50f28f1833c27]]
File: .git/objects/7b/c736963d6dacd9f6e3fbdc56a50f28f1833c27
Language: Unknown
Size: 314 bytes | Tokens: 151
----------------------------------------
x+)JMU063d040031QK,L/Jeheo!ּt&CU:0|7/sR_Jgg*J+dVٓY_k@"LE~Jj|b^bNeUjHm~B;M?kmreڔ<7خ$;6G&el97wɛBm +,N͋O,O,J)yX܂8P=Y#+/))J)mߝ+9>瓶\\bd.GTEu7̸~~e~/,:
 =


[[FILE_START: .git/objects/83/34ee7004349bdcccf876fe688218f7e7578e8d]]
File: .git/objects/83/34ee7004349bdcccf876fe688218f7e7578e8d
Language: Unknown
Size: 363 bytes | Tokens: 192
----------------------------------------
xQj0_?0d_Br
9$=Xd8̰rUU%wZv)	k{kP\[lzZqtB	V2a(`52kU9۶gCmDD%r	Ez=襛Cy½xw蚎;0Vє<z0ѻ`NѺ	D2 
.bTo5+$.$l%"3W5qj zYtu02$GL"y
=s[ۑX]9;Pe:FHJjИ3V'0mTs̘(C>5_Gd
_:΃


[[FILE_START: .git/objects/47/5035d6f821b18b1352f59ac5496ee5cf2d1cc8]]
File: .git/objects/47/5035d6f821b18b1352f59ac5496ee5cf2d1cc8
Language: Unknown
Size: 373 bytes | Tokens: 171
----------------------------------------
xmRK0m}е aPE|H=&17i9p}?Km	dTdR*&,6AzrEٰ(5qu-}BZjǕ5@ZkaL[p]PBAPV,Ap94=&E(4IdM>ap);ms#4;kj40W =
<|Ve1N~>qO"y>(aZC閣	KR($Ole]b(NX8:4
$YP|vCSrrx,W:{Di-z-(nз


[[FILE_START: .git/hooks/pre-merge-commit.sample]]
File: .git/hooks/pre-merge-commit.sample
Language: Unknown
Size: 416 bytes | Tokens: 102
----------------------------------------
#!/bin/sh
#
# An example hook script to verify what is about to be committed.
# Called by "git merge" with no arguments.  The hook should
# exit with non-zero status after issuing an appropriate message to
# stderr if it wants to stop the merge commit.
#
# To enable this hook, rename this file to "pre-merge-commit".

. git-sh-setup
test -x "$GIT_DIR/hooks/pre-commit" &&
        exec "$GIT_DIR/hooks/pre-commit"
:



[[FILE_START: .git/hooks/pre-applypatch.sample]]
File: .git/hooks/pre-applypatch.sample
Language: Unknown
Size: 424 bytes | Tokens: 109
----------------------------------------
#!/bin/sh
#
# An example hook script to verify what is about to be committed
# by applypatch from an e-mail message.
#
# The hook should exit with non-zero status after issuing an
# appropriate message if it wants to stop the commit.
#
# To enable this hook, rename this file to "pre-applypatch".

. git-sh-setup
precommit="$(git rev-parse --git-path hooks/pre-commit)"
test -x "$precommit" && exec "$precommit" ${1+"$@"}
:



[[FILE_START: .claude/settings.local.json]]
File: .claude/settings.local.json
Language: Unknown
Size: 447 bytes | Tokens: 168
----------------------------------------
{
  "permissions": {
    "allow": [
      "Bash(ls:*)",
      "Bash(git clone:*)",
      "Bash(mkdir:*)",
      "Bash(chmod:*)",
      "Bash(find:*)",
      "Bash(python:*)",
      "Bash(pip install:*)",
      "Bash(source:*)",
      "Bash(git init:*)",
      "Bash(git branch:*)",
      "Bash(git add:*)",
      "Bash(git rm:*)",
      "Bash(rm:*)",
      "Bash(git commit:*)",
      "Bash(grep:*)",
      "Bash(cp:*)"
    ],
    "deny": []
  }
}


[[FILE_START: .git/objects/d3/b9ca32e0ffb71102e8fae662aa80c5f92d3803]]
File: .git/objects/d3/b9ca32e0ffb71102e8fae662aa80c5f92d3803
Language: Unknown
Size: 463 bytes | Tokens: 244
----------------------------------------
xA09WmiJ UZĞ$#b;뙤eg|Y{k9A]UR {
(o})/iGU]lVf#r	e6ҕ2|E[č65
pJO%xKk{:Zko߁z[+UV<Ϥ*o:zt4bUp>eǠ[0tڻDqGR2NXohx7pEY ÇٟDg
t踥#'-dB]fW&4١&/1uL^[6f8Y
4SdG1>cFR2ɃD&#O)E8qb.aFZ@GL%f?
F;µhs+_B#{Q\<%kBs/q+δZő4pzOr(e  


[[FILE_START: .git/objects/b1/28da43ade9cbcc07aee9125f813cd5f7de20b8]]
File: .git/objects/b1/28da43ade9cbcc07aee9125f813cd5f7de20b8
Language: Unknown
Size: 473 bytes | Tokens: 235
----------------------------------------
xERQ0ٿx<"v!'mBUzmXVݮ/vtbu_[GmyFh?mlJ矆_P2N(`$PWz;Y
>FKёX`mkK<.7:p`*	Yw%(2x#kS/!y 
<iWx,֛T<~s%pV$@U(qVkEDJ"gKPM[Pme
x>jJP[Ol?p{jt0<L6O=؃50gsW:l83O_'naF}[,dnVN*VIdlKFc>99Z2I6חKν"34[ȎLI¯S
1DGyylYZsdH%m1\s*; 


[[FILE_START: .git/objects/6d/7b5d68acb61dddc3107d1ac1eb298189cf1a57]]
File: .git/objects/6d/7b5d68acb61dddc3107d1ac1eb298189cf1a57
Language: Unknown
Size: 473 bytes | Tokens: 216
----------------------------------------
xS]o09b"xˑx$tчS?@!{dumM
UHPv<;;c76GG̼-c8 =9ܢY47q{
g[2~٢zs)W;n} k
Zb' n,.anz_h
O?܃S?$FS	u;wmA+4('0mnДQS	޿EDdQU(t!f0h0ߝ27C])Ë/k:4)}
(8v2,Sf
!+$l2-M௪qìc,I,$ӐU{K{bN&es}SACHPI4˴:1WO-Isd$L|]'().*.ǻr?U=&


[[FILE_START: .git/hooks/applypatch-msg.sample]]
File: .git/hooks/applypatch-msg.sample
Language: Unknown
Size: 478 bytes | Tokens: 122
----------------------------------------
#!/bin/sh
#
# An example hook script to check the commit log message taken by
# applypatch from an e-mail message.
#
# The hook should exit with non-zero status after issuing an
# appropriate message if it wants to stop the commit.  The hook is
# allowed to edit the commit message file.
#
# To enable this hook, rename this file to "applypatch-msg".

. git-sh-setup
commitmsg="$(git rev-parse --git-path hooks/commit-msg)"
test -x "$commitmsg" && exec "$commitmsg" ${1+"$@"}
:



[[FILE_START: test_iteration/iteration-brief.md]]
File: test_iteration/iteration-brief.md
Language: Unknown
Size: 504 bytes | Tokens: 124
----------------------------------------
# Iteration Brief for AI Planning Agent

## Previous Vibe/Goal
Create a modern web application with great performance

## Changes Since Last Iteration
- Modified files: 0
- Summary: +0 lines, -0 lines in 0 files

### Key Modified Functions

## User Feedback
Please improve performance and add caching

## Previous Planning Context
(Truncated for brevity)
Project Structure Summary:
- /app
  - app.py (Flask application)
  - /static
  - /templates

Key Technologies:
- Python Flask
- JavaScript
- CSS
...



[[FILE_START: .git/hooks/pre-receive.sample]]
File: .git/hooks/pre-receive.sample
Language: Unknown
Size: 544 bytes | Tokens: 169
----------------------------------------
#!/bin/sh
#
# An example hook script to make use of push options.
# The example simply echoes all push options that start with 'echoback='
# and rejects all pushes when the "reject" push option is used.
#
# To enable this hook, rename this file to "pre-receive".

if test -n "$GIT_PUSH_OPTION_COUNT"
then
	i=0
	while test "$i" -lt "$GIT_PUSH_OPTION_COUNT"
	do
		eval "value=\$GIT_PUSH_OPTION_$i"
		case "$value" in
		echoback=*)
			echo "echo from the pre-receive-hook: ${value#*=}" >&2
			;;
		reject)
			exit 1
		esac
		i=$((i + 1))
	done
fi



[[FILE_START: .gitignore]]
File: .gitignore
Language: Unknown
Size: 743 bytes | Tokens: 50
----------------------------------------
[Error reading file: GitInsight.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/hooks/commit-msg.sample]]
File: .git/hooks/commit-msg.sample
Language: Unknown
Size: 896 bytes | Tokens: 252
----------------------------------------
#!/bin/sh
#
# An example hook script to check the commit log message.
# Called by "git commit" with one argument, the name of the file
# that has the commit message.  The hook should exit with non-zero
# status after issuing an appropriate message if it wants to stop the
# commit.  The hook is allowed to edit the commit message file.
#
# To enable this hook, rename this file to "commit-msg".

# Uncomment the below to add a Signed-off-by line to the message.
# Doing this in a hook is a bad idea in general, but the prepare-commit-msg
# hook is more suited to it.
#
# SOB=$(git var GIT_AUTHOR_IDENT | sed -n 's/^\(.*>\).*$/Signed-off-by: \1/p')
# grep -qs "^$SOB" "$1" || echo "$SOB" >> "$1"

# This example catches duplicate Signed-off-by lines.

test "" = "$(grep '^Signed-off-by: ' "$1" |
	 sort | uniq -c | sed -e '/^[ 	]*1[ 	]/d')" || {
	echo >&2 Duplicate Signed-off-by lines.
	exit 1
}



[[FILE_START: run.sh]]
File: run.sh
Language: Unknown
Size: 950 bytes | Tokens: 50
----------------------------------------
[Error reading file: GitInsight.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/hooks/pre-push.sample]]
File: .git/hooks/pre-push.sample
Language: Unknown
Size: 1,374 bytes | Tokens: 383
----------------------------------------
#!/bin/sh

# An example hook script to verify what is about to be pushed.  Called by "git
# push" after it has checked the remote status, but before anything has been
# pushed.  If this script exits with a non-zero status nothing will be pushed.
#
# This hook is called with the following parameters:
#
# $1 -- Name of the remote to which the push is being done
# $2 -- URL to which the push is being done
#
# If pushing without using a named remote those arguments will be equal.
#
# Information about the commits which are being pushed is supplied as lines to
# the standard input in the form:
#
#   <local ref> <local oid> <remote ref> <remote oid>
#
# This sample shows how to prevent push of commits where the log message starts
# with "WIP" (work in progress).

remote="$1"
url="$2"

zero=$(git hash-object --stdin </dev/null | tr '[0-9a-f]' '0')

while read local_ref local_oid remote_ref remote_oid
do
	if test "$local_oid" = "$zero"
	then
		# Handle delete
		:
	else
		if test "$remote_oid" = "$zero"
		then
			# New branch, examine all commits
			range="$local_oid"
		else
			# Update to existing branch, examine new commits
			range="$remote_oid..$local_oid"
		fi

		# Check for WIP commit
		commit=$(git rev-list -n 1 --grep '^WIP' "$range")
		if test -n "$commit"
		then
			echo >&2 "Found WIP commit in $local_ref, not pushing"
			exit 1
		fi
	fi
done

exit 0



[[FILE_START: .git/hooks/prepare-commit-msg.sample]]
File: .git/hooks/prepare-commit-msg.sample
Language: Unknown
Size: 1,492 bytes | Tokens: 433
----------------------------------------
#!/bin/sh
#
# An example hook script to prepare the commit log message.
# Called by "git commit" with the name of the file that has the
# commit message, followed by the description of the commit
# message's source.  The hook's purpose is to edit the commit
# message file.  If the hook fails with a non-zero status,
# the commit is aborted.
#
# To enable this hook, rename this file to "prepare-commit-msg".

# This hook includes three examples. The first one removes the
# "# Please enter the commit message..." help message.
#
# The second includes the output of "git diff --name-status -r"
# into the message, just before the "git status" output.  It is
# commented because it doesn't cope with --amend or with squashed
# commits.
#
# The third example adds a Signed-off-by line to the message, that can
# still be edited.  This is rarely a good idea.

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2
SHA1=$3

/usr/bin/perl -i.bak -ne 'print unless(m/^. Please enter the commit message/..m/^#$/)' "$COMMIT_MSG_FILE"

# case "$COMMIT_SOURCE,$SHA1" in
#  ,|template,)
#    /usr/bin/perl -i.bak -pe '
#       print "\n" . `git diff --cached --name-status -r`
# 	 if /^#/ && $first++ == 0' "$COMMIT_MSG_FILE" ;;
#  *) ;;
# esac

# SOB=$(git var GIT_COMMITTER_IDENT | sed -n 's/^\(.*>\).*$/Signed-off-by: \1/p')
# git interpret-trailers --in-place --trailer "$SOB" "$COMMIT_MSG_FILE"
# if test -z "$COMMIT_SOURCE"
# then
#   /usr/bin/perl -i.bak -pe 'print "\n" if !$first_line++' "$COMMIT_MSG_FILE"
# fi



[[FILE_START: .git/objects/82/f927558a3dff0ea8c20858856e70779fd02c93]]
File: .git/objects/82/f927558a3dff0ea8c20858856e70779fd02c93
Language: Unknown
Size: 1,562 bytes | Tokens: 771
----------------------------------------
xVߏ49CNDP㩽^᪶Vd}vv/NV}axf<mGO`/(KalYͬjP۷<{e?m,.vS%4(.Q	P
T^5c+v{kfTV}0d-Y\?qő8$s/k)%(l]Tʄ5^GX*޽xnf
FhO,e93[Wg8 ruF98ͣ$/,VYA Hܰ`2eim!lcnT'C;)(sL>N*4nWlOi7D\Gy/">Bd.{|M.jEK	.{Au\fuiVj?9:fP>rٶ}ds`Ʌ	mw8v3qB[aD.k6UK(ܼ#$":X1tPiѭp혒[W枵V41DPfCi;$KOMb	 G{	CHY콍 ̺4;VRls19o`wTe;aMz:<I#{m=ЉRO\dG6~ى p
v
[Ёd*$J#?
F9
xPFs }R 1J[%BXBi79^XxXZvCAzD[(G8Pl@*{!y2LpT5oOWBFM%`D04B@i]ϓX&
\\0:
aCxA8opC6Aе.`+f#IH2)߂5ص֒^%W_Np]Le3 @ vQ(iøi xе[3d[F2q1^}juD9_}AT,Q̊PTF ]4Xe Ķմ&$#0zHyR~1Cvz.yr +QsZP{M
=s BgI<fl2Az?9 +b=
PBWրpםNrTc:蹃^c"McZJV9Ւ-= )B|1[u/~uA~;>X5eyD	}c^ ZVY'zW1hÄ6RwUK.WCn'j6M^e. n4hӧE`س0
ա%aNWxJ{#KAL,"~ GpG@(;Uǹ݁f78^n`d>
1~`K-?onNdEx
o
L/jĎBK^ǻ[];m9#agOsW='v;A8 ^ ъu7C


[[FILE_START: .git/hooks/pre-commit.sample]]
File: .git/hooks/pre-commit.sample
Language: Unknown
Size: 1,649 bytes | Tokens: 50
----------------------------------------
[Error reading file: TodoItem.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/objects/cf/0cd806d463f6892ec69d794bcc2f98a51957c4]]
File: .git/objects/cf/0cd806d463f6892ec69d794bcc2f98a51957c4
Language: Unknown
Size: 1,688 bytes | Tokens: 843
----------------------------------------
xXnFYO1P$h؇ɩHE@fC-UmA0P|I:S(!wfogfgyU7W˯m_r/ghmů>j~nUv%js36enS$JeeU6W7KJ$prAV{^8A2'aUW2%#)C02XM2t[hZ"%K(ɖ*>a=to)"Z܅r¹PѓiyE
`j'5VZ",. -=㫦"o'45]upQ^1"y5nVku\'`ONm(wY6~;񱺃PL"B &;vRKX%Nl4Mu,㱔ktV1+[tgkluWYQ	QgW
F<5F<"QMe'f\L	bkt
a(c)A/猪:Y8L$NLJl^۫".V%ɘgSqoywI_i2'IA8J
A{|՞;T:#M#$׭Hn%`!MU;	MwSX-`pڏrD[\Gꇇ963ASh/0T?9Ͽ;χF30zJ1B\<f&xHJ".CSx3?W8ҺN ɝ &iRҜi&G5Va[RM/'4MJSAO׌C!br۟/ 4;vߝ6܆ZhZ:fm(7M}ySwA13'uWjLyrN3%x+pdx|?Y8Bp{M_UOY4"Dzw;12H6W'
1+8Ii?w%&.UO7q
3}G&lM.x~23[XڦNJ܏҉Z+ؠC
pf8w37X9K6L;dg	: hx0)VХS K/0)1pq7c_)#9|
/29?3vӫCi'#2G&:/oSbEe 4~Yp1hzձҳVk}3/5'gk!Ơct&F0<f}
𥳐X!|<F7d`2)S@wKI;yXߨ#^Yw_%{u
UU(
Q}Va%:װ!z!4]w3}`UQwc}tߘ+	b+A#:5M|ro[3i7p֘DE;ޓ8Q-c6)E<[wϤQ:<VW4,'|,,<=aXwcSg˵8@:^M{
d.!$GJxK
 R܌N/<q]nm1NAlS*\biMư l=I.FK>ts{-dsœmbL~erW+	C'ȟ.||˲N,2esÑY%V"


[[FILE_START: .git/objects/f1/4f37743bb30cc92234fe68a93fe6ccf50dab0d]]
File: .git/objects/f1/4f37743bb30cc92234fe68a93fe6ccf50dab0d
Language: Unknown
Size: 1,770 bytes | Tokens: 891
----------------------------------------
xWn6b<46r.Ci NR	悢5Wղ撪HZ)
?%=C]V^H ɒ̙ùqsz_ݡ7\::q6
tZJh*z%ܪ>IܡWk֚7In=ߜ.,X),֜' EujK[|k[6|H+uYy
Le4
 9[T77>
*RJUq]먪`zlQ+x[4;srxb2ei*M޷A } Z&<@SK6rU+F'1pU
ua퍌"CoؗOiR"JWVE|:g匽WHlO*L9g>Tu&b(Z" lmFN:'5X@)c)Qy $no\LIoB<Т(º),@%5Pt(XF/I$RefC
e$48*XvWdkU`DśXj" CzhWa:rJh	MVk/~uvۖ\WR<]XYU9\],P.g#*+^|L*wsD'DmŽhIr~~MXҲG> G3T1=B:̤VӇc>Y%ڧ4M?F()ʹ0ٶ㹱$:j͹
+Jʤt-T0~ֶgHGd?ڽlE.zEi:
+$yzRr$8
Hhy$Ѣ6Fi@Y[^Cmdp3WTfKmH%rBDbPO}niRb\pV w~sty/VoNNdrOrD>_]eʌK]eF_MD:z_z@
=ʥ%zz{O݉qKZ>j_Te;![FA4k1=4*8IIt2f7qw:͔|i%K&l>3U73-)2J<&$D{VxoJ{aҵ̽Cx&'{齸*3𤗊V|rB@8MxP+CmH ܮͮC>@Ta6g=:h%~nvĹ}a#혒[)$˝\v,?*Dmz`%_(
^Z
-ѣ	GEZ)JiQuCDs]*HNy]~GJlJhCh[9hF_}0i'
Y#f+ҹ1 먽G8̏1u.8VC[,"pX7[c#cGQ7"QJb<s HzD2d6X>'9/TK:xFM;gpҌsZ7E20Π)4CKɬʑroP9<ib9`)	FFvww
#<@^Rc,2X7T΀/불DQ
	ʾsPQ_Rl8٧(UaU_k}=8jCRGRxXϱ?l


[[FILE_START: .git/objects/56/426b89689759ced8f6fd3a2a4b6a47689de44b]]
File: .git/objects/56/426b89689759ced8f6fd3a2a4b6a47689de44b
Language: Unknown
Size: 1,772 bytes | Tokens: 884
----------------------------------------
xW]s7;]	!'3i]W[Ik{v0$ٽ{v͘}=yz$RӱpIKވ\ҍ䧒>X>qWN,7~Vk1n;|J)Ѫ^:b+~emrp!AN/B8N$/'/CSHh0,ID
_[$VLHT5BZskrVEB	v?b8X*!H.\n']}U{$9fBsXfYj#1oKM6@qraJS@4G5\/!Jy$PvGG©<eʵ
RSyPyƇjֱy(udW[u1D_縤	+ۄ54Γ(q[Ins%NGpWNq5Psʀd5)
BG6%O׌A~<uqH
/9'.9h9	0̔ʯy~Tٜe:hsǦQe>4`渟" ū%{O@!&R-e4`+: *eiruUaeC0{ޡc-Bvh\p"̭pSOEr	Ѻ9$b+a<Vh0Btoce'B2%rIa$2e+\v$aÓvśiFM@TJ,sp !hJ-(ZـppftQGUU{V~ʰ.ejƳvl R,pm{BN1R=7rwW{v>%	lނ܅hOl٩kqށeTM4c6j9be6:t)(v]ĴjP2*`zG52q̺Y8I`GJ1l^76)|$+9>T?T@&
.!0n	oN/InȌiٶ;ՔA;	ЫIi-	T%ێə
z/Zp?huCL:d__}?AOvyx'O5x`ϳ>Ϗ8(^ltaǚ<Xh>4XszNzΛIM`˙ZV@˓V6`G{*z_c.vHPyESA
z8R*	>RxA#46V<rln_5+
1ki	ִĆpGȆ^A'-@Unvvi
˒#Z0r	7o{:7;j}z9`F
k[UAԡ,0∑nWvK?wKJH/Hu_!cX/ eȯ9W.3b
4$[[(,;
&*aP`<ynb0ܯwtUseLNoKXߒ_K[ؒ<dq80g&>rk6dɴTv :0<q>Ύ_:6|V%NLxr-PL1#ǿ0iM޶X#


[[FILE_START: .git/objects/af/149042084ab176a92b33fe531a02bff6d6b2b8]]
File: .git/objects/af/149042084ab176a92b33fe531a02bff6d6b2b8
Language: Unknown
Size: 1,902 bytes | Tokens: 912
----------------------------------------
xYmo6,)`Iv]*hE|ا$
$$+wwlڑݷՇKZ<G{3W	@!8UD
R_RJ' 	cGg8bUR76.LWNV8Fn6\e2 TEl3Qprr^kUHHWsiPUN;pU5n$/Kk0GΤDafF^1WX'vp,NfObq!|H6y#$Zs5֎#RSJV6͐~	'UX
iIokf@ujdT/a$
[WUݸ)M͂`]fqNW)pT
ep"qD6"&\IFau!TYƸr4)\?GLFL`^aUk*_x,SsX)D}zgZ1zrl~n@rL<ӤK6G"k~BΛLkҍ%1
F@XKMTF !/K3_Pr(Eź>d/xZ!U@s4EkӺ1E+C8</+ / WK0t9j4G4a8_a!u_Tu+Dge)pގgtG}&`261E֠܂e^Ah%\Wjht~0W/Prm	\.ZbTdײBM`md:
!}FV)~8CAr,n+y
НN\S_.UeEKص5zk$ aw0ۇ8^ҰiNKp	"
]P>>*x88]d6uof_hxլ]+AtjZiw6(rF_DR̦\9D|@̅B[kd @7`QyOFgf0..u.]y3\09/NXMv<8#"3M@.^+J`nv37/gܽ`^`pF,}Oć

iO@-2(mSael%(­ϴu 7?yOؙn*a ,3fYel}_gf&FpGyb歫$s=u8Llh
}IEI}&DxKbjt6]8B[SXwAD}5&E0UAG_
U')|(3Æj0;x۳h1-{섢	.$JTMb!n/RUh8z]z2b
]=m
/>eD陭PftyE* AJz-ڟr!W0(oVѸ&W`28geL~:%Q!{r>fNBtkN+8Ϸ8kZKs8LY(FZb֮aI.5":Gy[\2MrYGPe+턛8s|wY>G+Tc<ĝocv~y>|PV=J6hbLw!LϾ#QTӮ%ME,}oF}{tR={WcF[	3\v_[})1mrs֛LjG\PX,.̨@&dLh|ӶY{~>oqO


[[FILE_START: .git/index]]
File: .git/index
Language: Unknown
Size: 1,928 bytes | Tokens: 1,131
----------------------------------------
DIRC      h)Ǒ(<Jh)Ǒ(<J    u        (C_<  
.gitignore        h)Ϊ8ih)Ϊ8i            7aΜ\wv) 	CLAUDE.md h)ŭ0;;h)ŭ0;;    Ҵ        VBkhY:*KjGhK 	README.md h)ѱ"h)ѱ"    A        -)з/࠯s  
app/api.py        h))h))            )~i(D&d+=wEĐn 
app/app.py        h)Jsh)Js    ί        '_xyx 3@C app/profiles.py   h)Ь$fU@h)Ь$fU@    Ұ         KL2kL&5 app/static/css/styles.css h),h),    ұ        :{ȭAUWa7 app/static/js/script.js   h)ә-qP}h)ә-qP}            J4knPjKa7"O app/templates/index.html  h)$h)$    җ        C'U=Xnpw, repo2file/.gitignore      h)$h)$    Ҧ        >O7t;"4h?

 repo2file/README.md       h)x Qh)x Q            <$k`^HFlWD	{SEea repo2file/cli.py  h)ݒh)ݒ    Ψ        ,l`Fau5*rx repo2file/code_analyzer.py        h)$h)$    ҧ        c.ƝyK/W repo2file/dump.py h)"Xh)"X    1        U2hQ1KV40 repo2file/dump_smart.py   h)>&5h)>&5    C        Vp`^ fU0j repo2file/dump_token_aware.py     h)hh)h            s4͸MALfD repo2file/dump_ultra.py   h)H-RS0h)H-RS0    Y        jzYvi:vj repo2file/token_manager.py        h)Ö<h)Ö<    Ҳ         q䯮:.G!a0cLZ requirements.txt  h)h,
h)h,
    ҵ        m{]h})W run.sh    TREE    20 2
$q^`_8FTapp 6 2
-"HVq2K8
ZJstatic 2 2
*όsr}dQgjs 1 0
je^37ncss 1 0

bfz
aF苑`templates 1 0
KVQʩprepo2file 9 0
{6=mV(<'*A6%L_[|


[[FILE_START: .git/objects/34/6bff6e8ffabdd3506ad5f24b619d3787224feb]]
File: .git/objects/34/6bff6e8ffabdd3506ad5f24b619d3787224feb
Language: Unknown
Size: 1,930 bytes | Tokens: 948
----------------------------------------
xYmo6)`I-
IKТI>@IFr;J6nӮ>|}xwzx<BoO~J~>z{xW0se1y#YE E>y $t0Vqtq:G,*Qq4WE
^ƹL\Sm&
9vPNBNZVu5Y崹LUS1O#qdm!LJff8SsCS\"0v'
|D6y#$o[s5֎#RSJV6͐z^1'UX
iIokf@ujdT/a$
[WUݸ)Mm`]fqNW)pT
ep"qD6"&^/<ʛC̩r&F7٤p12
xU▯|MO͍cajwUYJkTnSɑSeQB13ip&ORO>,H^c`p~y)<.δ~!ݸ_]#nktpNNոez\4Sy.EڗܕCXO604/_+V2b(bNrhmZ"38z@Iǂvp:j{0y	.Gf<+,$
n%ؙYY )z`m'C	X$MBL5;on2
E q4NK5m4JF~T?YUK(9̶Gr.]x.ٕ/|yv)Ye蹎gvor5J7iX̠3 GO<Os"TMh?<3g2][<pv[A4܏}E{*+\ѹ`P}ȰCgo}fҋ-v"\NQࡅ"iV7Ž̮R}zGg[gLѽGVJ<OvЕ4"b6!znBu	b.zF|;F
th_|#Ȼ|7/0-qqsC˟QH 0yqh) i7 rTUw3yy6w?M93bixPUH|* jf,mFim
+fsXQFq^mn}tS9`e)*;Ld3:3313^k8o]%¶ГcQdXSҕO2 A3.}O"5Exyw?tHE{<|Ƥ*SA  ~a.WC(|B_9
̰Zt$vZL(^%;h®|>US:F%Əh8.kIoÆioHtp(iEtnt"P4<E39**7P
V.-Ӛ	U\:*dOǄLsi@VgMkTC8)(X\IL.OÕ6}eVD]gw0""oSkX-|ܿ/#pU]j
m	YL%) v9ZLUS9&mgϞ=I	Ejգfv&t};>N0y?:YB\_WĢMGmf>>տG.jh{+͵v_[})1m&tsڛ"MjGSxA4X>\:Q5^Lk ;m1 ns r>


[[FILE_START: .git/objects/d7/e07a6e3610a12f5416a7ef3f51c0238f0b5b58]]
File: .git/objects/d7/e07a6e3610a12f5416a7ef3f51c0238f0b5b58
Language: Unknown
Size: 1,987 bytes | Tokens: 1,001
----------------------------------------
xXnFb!?jdI
hQ4ioAȕ̘"Yʱ;gJF"EΜYnn#..^n6d[JVb/[S{1{uzweyv'ܳ_,ZCߨ7uƊWȲZ+ׄ[KUSY^xQw+xiR剠u)"*
})'9v?PKm:iEphɎ.ŦFHq|vXL3VZ)9gj]sMx~MR[yhL醇UEb9B֓<!i5Wy_da/떲ilPYA
<GqfC\2w9(-K0KMC@#zkM/aG F遬
DVHyv5TٴCc/0\#bR[$c9vOB̢]z\l@ʁYp*\-G/qV#<ʁiXA`c+i~e߫⭉,峕@'~L9h)
}W)w)]o~-Ҁ,b^BC@chH˪$)-ڤx:2}W}mf#[(Fj%o2NW,Q3"FצI*jbȕ}|)1~zQv8*w)18a-ŭ"R	4Wתcn4jsCTޠCΈXC<lVɯQ$A1A0\L.4em-}gZX'9/<O6p@!?B>5*ܾ%K?mSe{}ˮ54޸:Z_-颷\ǰP߸$Yva;ب	ӃDFQciXb,Z*~[6*!s{ɾ}X3[PbO5TK̅v$LUmbEPT8煆?ς	
B݌=h2Mxp60gi:h
E6ŇHSfF%#1zL6MI*+#okG=Et*nj5UAiJĝ4qTb.>כW$B;kffkPq4
7U|Gca4
 PSCG"JOvc]Py?̗beGy'IDNşJ@ !И):{b$ȱ#ez)	U{ث֌uOu"OPa
znQ{^tw4PhHGAe|&A)s.LzV(:Ē+F1;**3[!z:NTH)gA1|8i#\S2M%__/P^cOP=I]4Rv4JRqsAAY-ԥ"]هv9==/|)XyZG0H:;sC3'hv<3|` 9Kj`T|8%;YW~KǕ7&~i@ʱ60T`ՆKJ7qsT}~e  [؉wNghǇ#G`&Ҹp8OVe߂^N+^<ILtzA-8iL&g=!8*3+$/0*Z1tS5AGo1]&0%	iϊ8b?|&ZS=n2^mI)vGk`hy
Om߷]h'AKPvUMO&͠Z٧BH-q7̫þ^u,‌^`p
$8B6ب6*WDj(rg\D
f8zd


[[FILE_START: .git/objects/f8/b9c70dca96aa3d839103751a6dc0c27d382dba]]
File: .git/objects/f8/b9c70dca96aa3d839103751a6dc0c27d382dba
Language: Unknown
Size: 2,049 bytes | Tokens: 1,042
----------------------------------------
xYIo6ٿ$iGxr(z˥聒Q8A{.Jc'i6X}oQшܬ7;)"ɲN#Y)!wzM޼KVTҿY)Zx6q{Pj7|P^G8Qq
!+&&/ͺ\]*K~ےէoxzo;b/G ͯ*~
Q=CjѪGހ~f{ȯ?_AZvdE[OO>9-
#<u1oZ8S,LA9DQEZ!;Jew΄H_Jvԧwؓ`*Y4یB(%;n>,bod{e T8o֮_|ᔚ;)JhޱA?;Q@+qe@``"}ψ;_XGz`M(m7Whcn{f
M`1pUV!vL>0v~.OG,WBgptЦ!|՛
)8
ab	]q-kxdoI쌂112Џ:DjA	*F w)/64hEפ]Gf=#rPG}RHu4 kh7,3|Ђ5iV3vшrHi|[,#&1RCJ.\;Y)sEj;{OԇK9
+AR#a
S?.Eq΀L
P@'urIPA{"E7 qSx5*YV0uf5Y1|qrWGd:TRxŚw=6C`hdR߳90<9#sLm?ըƜ\\N	!+Ebސwku>F(L0S<w)GXaM&:K"6yǎy'5PS<gd8DO$LQP"Wym/7`Sr>ef0oFj	
Ivy q򆲭d
K- gPXc"advQa)9e2f>#av6^lE=XP;֦O
H7xpǐyy`H Wv[m2<ym-!}nNR%ql\*!yh	m[1t)ssq(exUR88U{S'jFz$ˤA̤mU=N{2ւL+7q>_]*RG]V/vzn#84z߿p_ڀ
=[]U0$Դ)Tx]]mD!2Yd`bL,Yg_d!IXt8H0¾Iv?;`I6;Sbe2Nm^k;,qM3P}Ln*CQVUArT07eAzhV".=%혣RA5B\IwQ19.時`lԲ5UIK
ΑB6m`De\`'Μ$4F5N8Jq}/a!]Ԃ,zK%୞Adc}W|4*:;IY@LZm:=qRac$`;gEP\d<KafI:͏C7ද55y5*B6ɞ%'ds1(w+f9ўJ+CPkiZ2b
TnadVʲoky4Xsmd0'efk>c>0{mFzt2!@K|q4Dj1#7-bsښ*W	&Y)y}B<!a:Mwo&32ksIr8q*.gt5|9莏+?]}b


[[FILE_START: .git/objects/7a/59768b8098d7dbdf69bff9c11d3afba1766acb]]
File: .git/objects/7a/59768b8098d7dbdf69bff9c11d3afba1766acb
Language: Unknown
Size: 2,066 bytes | Tokens: 1,007
----------------------------------------
xXnͳa?H\e;IAd d"1so$eg-:uSռ;wgGT}0:FߛiڵM~jsFеUz]}^g
V?Vڬտ:[x.j=fk⭵U.` |쇸LzBE9u]rK;Spƺ'=vWm_k[Dml`ǔmkQ`ưן影m@- %W7yo! Zfwm)!;󰝅u%5C׷ETAW
L[˷D|b{c}0եAxY/{Ȭ3$Z1R2v&9z	K%(m踪{n=vjq
OKpZjK<e,9lC,ug<4/387z"
g33CxmM2U7Ԋ<?UIiwtי\[3Y˯6jGV7OK6ϱ7l`c"|
*%X<.5D4 `.ԇA#tޠ"*pPUWQٽQ>e-IzP~{Glfս>Wv\@by	Xhchx.EC~)\oS֠1G_R'0݈킴\eFXb(&\DKtrWA(B{E?VY;4kFђ?pehd9lPT9G={pK^(hC<;O
7yz㗓JBmq9E?o!k1qPG>}?^ _Ke[d*yI;_DB1ߞ}=yR PX\W8f	$Bp$>]KYE~FL1%8 }%5ѾBXUyhI[=#i΢')"L= K&*'4
pET{@MyxΏPBs0G\ee0{<Dgc	K~NXds|423)~#xRsRbCa{ͨbb2;㸈.;)a@%8_R=~`2.]Rݱ!F݇i51u.Qhrs5PhhHGŷdζ~Ąӧ`M5ϩANkd'iƯ{^"4ȇu^1?!\ȁ"1DL;i46q,zsu2@VD9Lq|)gPźsۗ\#kgtop(=}<_Ih0-/ |2	ohB۠\XW8d"R41B~suⓛc%ـ-MwVOi{u"#şB; }^ooGndl:m.*:ռimUڝlY܉:D9&#'0HX~/n÷q@ Ga@'$(sJ
s@XȒS^0駱$jC'tdۆ	\zN
VХLxh|5~73ę粙4o,Ol0z[(ډsG|V/.E@7Bt7pӤ1W;$4kAW 8*L:1zX)'D{o3x%&&gW̌2>8?~ٔ	NSf3^lLI)uGgJp2۽FQ AGPn%02}ZϋOỴ_mf9:F-8"[H@#'j2B۸)ȉ^_p"]V2


[[FILE_START: .git/hooks/sendemail-validate.sample]]
File: .git/hooks/sendemail-validate.sample
Language: Unknown
Size: 2,308 bytes | Tokens: 50
----------------------------------------
[Error reading file: TodoItem.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/objects/4b/a3e4c2dc4c326b4cf6d9260b12d9c8d1088e35]]
File: .git/objects/4b/a3e4c2dc4c326b4cf6d9260b12d9c8d1088e35
Language: Unknown
Size: 2,318 bytes | Tokens: 1,169
----------------------------------------
xY[ܶ
" 3hc"@ї&})@IԈY(P=7Qfhx9|碬9W|#'IZT>'<نX-|kٱ\4\nmVIs{^Sp$^eBLMEQ7LJѿ`Mݻ绻VL<%7##s ͑ז^	(!hTR3AN~nN~89+k#O&:tI$/5oXR14,;wI[y$ť)fad~X
.%-|OɕVi:zQ"R|%YV1
'i(8LF1i%PJ$\-CYlh{e T8v֮_bZ(JhޱWzR҂_#98#jPUW YOd	&wؿu1фvEΊV1Vʚ
Mlmy:QЄfW%H,>ʤXܻ4s~2L+x"^|%!Z*x)G	k.֝	Ђ
17oނaL(EO}!E~!RbLPЮb7\>wR[Q|ۜ^AC$-&:/͜,"Ben-ugszr#y@zPf!%Ybf傑:@XtLb"&\q36b
!XGO؇K95"+BR"f
S?.)kqMLݡN>䖌}SkmPޤ/ eϵ_:Kqt	PΒ+cΊ	3B
=;$;Ё2,Wyq`3FO/EJÞ32WA^
+kIȅԉ꒙RD`:'i9L.a({%݊0{FhopޯenJ#c5Y!Zi'$B^jmj*X/پc3|m~+ZDö=rv,H\;[)j}̱N־z	jkL$n
?,=Lt+=[)/Pԁ:*9x`MRtw|YF.MwhӸ};tsbǔ.cY,!>ЬL">7遀G_Ќ uKqb%>uƛ
mGLrɸq,DV'C-ȴ2!{?mOo}e`bVK=Yor߸j(ÿ *`H"iSt-*Oaw.¶},20MrVa,37YaH(o]OF$`ΔX7TțRX6-7kS~?謧z(S7!S+UAtT0.F#DXN{n:-혣RA5t
&cr\7+P٠e$T/#M?Hmq?qF1j׬tOQdL|
{Ƞ
L
d$_*	od"\Jh:`'qߒOU0єBQޥ;H>5KU_'.O1ldu'W7g鶟Yzҳu>pך<{}6ɉ%'bs1(w+f9^J=G4:_K֒@e&Qn@яl*SYP˥ϾB<u0>)1XH+|Y4BNF#hI=2_ȱzZ/d"@j<gly{S7OgVpJ~;[~}#'1LndNymxNA <BnB'nI,c4Q_vu0AEw
_X
18͌T6Ik`?-j\{[`R߳,׹,,x(ݿ	M޴Mj9-p?g"X|,lBGk3Q[%#>r>z3w5BUBwn0ˌ-g[o:Րj-*B}}sTEXp r?D8+8|LV*Ǜ7lN>=+u2WTs6u0M_st?s;


[[FILE_START: .git/hooks/push-to-checkout.sample]]
File: .git/hooks/push-to-checkout.sample
Language: Unknown
Size: 2,783 bytes | Tokens: 50
----------------------------------------
[Error reading file: TodoItem.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/objects/cf/bb5982326c2008fad38ba4fd864d9f3a80bf3c]]
File: .git/objects/cf/bb5982326c2008fad38ba4fd864d9f3a80bf3c
Language: Unknown
Size: 2,816 bytes | Tokens: 1,404
----------------------------------------
xYkOWȇgyV+	ZP+퍠q{m`~OU=&du 3v?OU:LK?7o'w{n,F4s7+L[J<~mel$gtUsuqA\EWml탋YG'/*yBg65;jjbMYRak[Ln\[SWK[xҴ1)a}(W;zzIْn0A~oL<v5ЍѺabZL]O3Wln].7{'ր5Ŋ߱C>
/Yc)v$"4MM(I]ůocK^We'_ڻh+~'l%h0utK`2sk6_?bohs}Ks)). B;S>D2
Q-8SFx{wgui _z#srƓw#: @2s".˵׻Ц!6`Ksݼj}wC_?BBO$.m6L]~3*GQc=Qɲ%hyWM89
9E0s;֔_)ic3>7kB3GƸLQ ؊7q	~v*d$#m
4Umw$;ҝ|q=6؎$7!|h@_Hq6f)H)nZYK@<WbQ`|vi*NƼC4q#6w3Vz#wP1^;3J6E|j;1qki"8oPއ(z_⑉(U%CDfsvqh
CLRX<E	6UKfnTLǜAK	PD+^w4iL[[	o;-ڼZg_!ep=l
:^Yjj[eIK_1(
lXv
0Q>j0ȤcPӬd[//-N
µnt|BMe)G/0vv)]nk/*	NH\=ۡZȬCD'<Lx{r/m_9Au@#rb7F/]ItsZ!UfXd
Nr@2\._H`tk}Z}tnCW I 	g)i&uxAyÊ|:(K{@?:OEe`|aP0UA.lI|*H]g8@\,p##%%;hD$vwZ3~W-D"Wаs!,pup^1CG3kVRC=P8!etrnY'!$<;ԸY5ǰ%hyj۩ۦ,M{FDa@:yP21='Ag"^K50`7ݡT):nƢoJKy*V=w3\U&=hҫm^!&!o\ǟWwq

P4f+OI0
BF=>#FlV`h#}p:`
[qiu|Pɞ6о@5H<M%zn>LDc?DDܼ՚@9:[MmDM^Zc?BsI[*UFŧ.ïg-kX6~H뜫<# #
aPv~;](IfAz{4zڻa7C*346됇{r(%#sHqWumx^C \u8j'ijr6AABM6Pco	~c_ kkK5|xT)W&BH8bbGQiԨ;mQ3\ߧ7 
EIB5͚a2e	Nx kR040cIPP0F4PP/{p')aEء3 W5}_9ʜͤH^QDt<bXS=LGO\ݫHm@x
&J'ԋ;L~Fo|A
CQq+;=rbUŸ]lssS,{O,;f	zײre|@\B
@fWzUa%9&,ށϗ|%-ʥYn]F ^nXC!-.<ڟЈ&!(sK楙gENDlfpD\+LvSJo5=omsŶw$5#Wp~+:HIhhp2
T|c[[)#-WA'u0$ƖҌu&	ΈfJiɬM6eFHmF0 Dkv?Q;TP.uJ	[ #h%Giׄұhf>GeHIH=<,RkǨ(xA~So-na]2ӧ2w8zUGN+5LDO&&i(D}`7q<3
h߬]$qKJ[b{
4q4P F`ܗAHeuaŐEsW }j?#


[[FILE_START: .git/objects/37/61ce9c07afff5c77cee476fbd01dbbe2e40529]]
File: .git/objects/37/61ce9c07afff5c77cee476fbd01dbbe2e40529
Language: Unknown
Size: 2,827 bytes | Tokens: 1,330
----------------------------------------
xYmOH+JC3y?	V" ^t'Ect609B:m$Ȍ/OU=T3-޾}OhhbxYFhJKuo\a[W*=핦-,yظIva+͵t9"}FO_.MUllkw:mԄ	V!ֶ*l;%
ݸ&$[ᓯi1&bSQvF*.|%`68?L]51yt7&Qjg
,u8Ŵg\`=ݺ.]nN2ӭ)k`X}.D_
RHEi6-Q֓&Ed_ƺ˖˃;?wV4Kaɾ']k[e4M9.my7,д-6>>2Rf]]Av,}dN13Z#p|.P,҆AnG6;'%FuA+Oe@E\kwMICJ! ;momH.y~xǇ6N`q+H$E]*m9(fUp{
eKjI:fMprs=9`v!)6mS"zg2)}nBu͋B3GƸLQ ؊q	v*dO$?##m
4Umw$;ҝ|	q=/m;!HnlCvN/Ч/'m̈́SRuݴxĢ!6OTyhv&<Gmfgbvm6v4zgc)E.EqH3ߠkQ#QKj8xDYQZm82ґ-♎9(	WhbL[[	/;-ڼZg_!ep=l
:#^Yjj[eIK_1(
lXv
0Q>j0ȤcPӬd[//-N
µnt|BMe)G/0vv)]nk/*	NH\=ۡwZȬCD'<Lx{r/m_9Au@#rb7F/]ItsZ!UfXd
Nr@2\._H`tk}Z}tnCW I 	g)i&uxAyÊ|:(K{@?:OEe`|aP0UA.lI|*H]g8@\,p##%%;hD$vwZ3~_-D"7аs!,pu;p^1CG3kVRC=P8!etrnY'!$<;ԸY5ǰ%hyzW7۩ۦ,
ۥa:ψ(HH"|Fx涳4 Kċ&;t!FG׭XX{2bOūr&ǒġGzM*9$$䍫KU.@c||P3pgV4)sFAȨ݇uWA345="hg,XmV\j)zAg ?T§
Og
QC7WS&ǔȨZcR>>^8{KԕjKkRhO9`K54P:Y˽7+R;窪F$ ȡX,]%.eNJR@,C~°a
0':nt2(G=I
e7r\2p]KzY׽};3n]-	m=vMy4-l9[>{c-ҥq
Ug
ݻ.J<¹.V$N
/
4TZUZIM.dHCQqfp|YpBC&T&̺@d}
-!!Ƙ5F;5 ܫxf
DXv(́ d:UCX2'!z3i+ׂ)$=]ϥ٠Tt}IpK{Uɣ
WAD)z)赑4Ha(*ppGn]m^qvn*eo㉅L2!Q?tLGc"2@p:_nYE^'}ADXIwe(_zIci+Gkp?`֧; |72TAи'*4"	A{iYn{3#@/hִ`e`*\mmv48Xv
ovEIE	
NX[G*uiol?ck+ݺ}xe:,R@43ׄ8AS8
<Rɦ
Ȑ&qG:pԙ

cمNB)a`^m(P:M,]I
BUż[}  {`jŭ@TfTGH~_ikF W ,f 5gA"U  V55npi	BcaPpρv^]
Ґ ,B"2?hw
d/o\u


[[FILE_START: .git/objects/15/898d838a481f63fa5ab37c1242b1c744f201e1]]
File: .git/objects/15/898d838a481f63fa5ab37c1242b1c744f201e1
Language: Unknown
Size: 2,844 bytes | Tokens: 1,434
----------------------------------------
xZko8DAv*iAq3HӠR,щjYҐrO>^zYΣ]E^^syTgi>?vvvlTX&y&
ϓTj1ϕPȟ#5GR$;ИdYu\*_",/d&lS<p~DX'?4u~qXQj
%i,L8pqdTj=8Ob"H"_H	ϯVѣ[/7,B%ROy
u|u׀J#1%`{.ХXH%7bA2M?jP;B<0CE/d6 K,*>H~٧_ܴ(0%YbRL0ߠ$03Cb?3u)3
[yԅJrd9,*rbt4X Y A[^J<),W9 kL@Zx vs)\PO&j(YT&nX&5	yr}_7lj4u:9^ty4&׭CC\n{gX׺ܰn{gXǬܨNsgІ9a/:[;Z+bofoEs9gcmQǂ\Ẽ*m>%fTR+
ug쎦nzEwnmpS2ΌUy!aSXxWHԝjY:|{G!cb^m!SP Bo=lժcLp=4ҮW2Y^\>E=lPFPYtgQl]N^}Fon0&Qvޱ~(;S1|fI$P!
8ZEx&i83nU[R.M8^sfÝ]cDgp8=zKv1"dOqME[FxGV3K.$bXA)ћ|jRȩO<=:a~4}\Ini\Y=_Ct{$%=|3[%iw2ɬ&hpoww/ʑf}ߘ /ٶ"UۿՙoFHDZ[#M1 	 ZwU-YMC?Z :
L¥.f2TN@'ȖAi*URLP8X!Dfe>nf-"s
I&E*CQ]ڨf'qiM'
f9Ku63mZt֢E#5ϻ~HŮx"e^K"D\=&Σy#.ZQk@qk6;1M.$
Sq<57r񢇊el%7:)g>p{7'R*{Ck,GEv3	ȸDL8JWT;&5dneY\1blE'5^H<րm4;PjQ"~Ju%CzDۀmWM`("q0Zq̈́.l{!SZG/>°2/L_UK"* ɒ2~Hsh!
r{Rԙ_Wzt_ӘFv
, [sƩ[etgբL8a=rqQe{BN^+Po'}pvBbRwKVUJq1[I#rU{M-fk>ykD'.h2.ˊT6^!pG1Nu싺 Tl`UV7N%T
 KuY2\є906AiSbe[5};npŒtfY;%jؼ`t߀SgQ/պ@bY(zkWӣ}#\/wG}4Tgn$ rp޶rFZ6g7m	EM׭YEyucMW;*\Op9sDbvu,QUΖ%7μNޡfN9
E&lk(Vkwy9׳
S讬{w/+Ckm:YRy#5oDHϯ58Sr5@7Jx7$åyr*x"0hFށMIr#AP>٠TKKnv⣋N,;bP
yLĚYy%-Ti/A"H&xc"vOvm,?lWYdhR貛*h;
S-!NԽ
RM*Bw9_,qL?dᆖ׃MȀ?c(->Npdr\O=JxoDFem*c̓׮?|UʡG%Bq`~\(v`w-HeXX܆[5671^<]('StYm>OCi=vj?wQf
Lӏ+.;Q&FhXT# Np&}VD7@[gƢYcꡨ@ҪΝc|OgR1>؏
,PvZݞ~8sl=EL6D`֡G4[xe\a'"z[ۈUCۅձO":/`Ȫ%Tz>Y==I
Q


[[FILE_START: .git/objects/60/bf4661c81275b935f32a72b5781e94c204abd0]]
File: .git/objects/60/bf4661c81275b935f32a72b5781e94c204abd0
Language: Unknown
Size: 2,996 bytes | Tokens: 1,462
----------------------------------------
xZ[o`@j-s
iUh&ڠޢJ"	rK~̍CI j69<s/3sQ_ٳggrUE^/ȪYbY,RV
_,e:Ū[%NV,z%}ST |[j,~,:=~ݔr,sL]Ņ^E̺Nv@8OowOO~l%'S-J&ġxF4r]1^ME)#ZL;jBcZl.݄Xa鹘Օ9ZBY[^ gY֙Irg!"MSiQ*Mchb9LcŒtL+<AnM17T]URMv@/L7-H?QG<+K{ȶ ?tۢQC`	LJLhXqb.Rǂұu8~-+F"ӎFm!TX
1ŴrYAnD%e}+[hB2	=jVur1c,ן"hȶȵ9L׬4b"]wq9{bV|l%qk0辪+QJ	s	wȌrigEyYyډSLb59o)}+^nft4)M	uBO0L3p'64NzXPC!3Ra$J>g]_ӱ:+R^̠1YZgLح60`E	l42Myvv6d(#XIǭZHS1lY{}ydu%Ҏ	us\Y
7\?iҾO,
n&`l.7c
zk<~c-ee3F*v淳swvdZߡrA5UXro2΀Ca~C`Vkth
ʮ%b`_a{0wfPyG`9ni|].%+}׶uPxB(R.EɅVP\+e0S!3yPZqvaT 0O@i3P/j?_4JWmzyꪕR}Sd4q!Ӌί몾RC;4PW*+N}#M+ v$tq??5yedݗI\{WuTQ|~{4:ǺK5uPOWjZpyLeg'mnS/uBNq:㌠/$[,b9xc}pXkmїpKt5mIT3\Iה^j\h)!0z(KOШձ\5~j:
q<"6fKS^ŧj!u/=$h&5Uem|GvG/1T .xc)@Yy Ixvp4 n.Svv$Ʌ4>,ı0/Kde'`M6wPު=kqb:Ö}hx{2e޷Cq:@y084IN.0yw*~3#:(7ZίqL>+דּbl
hyđ8uQLbG͊4JVЖMfB=ÿuW<Ԟ. yn@"`()om4ۢѶMP^4PV"lvʾAS.ðx9%_w-lax<qS6bL
gc{N~AAsx<z6ш߼
V,(׷[=|2Zڜ@ƠwuLDICt BՀ@C:=$&{oe.i>0t21Ze
lO,f!g' iz  G㭄>w,}
$^=;kO3(1ǫƄV=nl"r QZ/5{_`'rur׉Y_md1o?ay40` s1]NG
|(
I4+qpj5S4D<^Pke+5*.Rd<^c \)wK߾w%sD[o+燧B=N6mqkrbtpT}{vI!	?igM
'Up1K(0˧8t|wiPy]&_8oS>Kyuq/9"R];sz\{a"lRi#dhrUH6a׮A)7뭤-!!HcRD+	nj?sm̀wVfAdO(NR5]rgޟ%e#m+?>
ㅻF'MTFmWG:CfP΁n-%ij`.qL7[Q/yFl.! b]2EGt;v_p(4WXdjśhYʊΑ]jxE
3oW7jGDWn>>	#č?l"(D)DtNb#&2ǴK{72̴U
}NYɆK<s }:,o*<ͪ0Gqz2+FfH:C:Mu13$|dC\Gj"̇W'<8HN%nאj'b:Qx}	5=\/H<x,؜h|R3S*iiL9)lՈnpCca


[[FILE_START: .git/objects/d6/89ab54575e81581a0390b284f9ee87dc9b867f]]
File: .git/objects/d6/89ab54575e81581a0390b284f9ee87dc9b867f
Language: Unknown
Size: 3,069 bytes | Tokens: 1,519
----------------------------------------
xZn>,TtצhHNv
k;?E$n(%V>KOgHJV "us,+f%Eܬd(I_˴V2U09}q^Q"ɾ7y">өxI"Pu\*=Sy-Kne&cUTYLB@T>Gmv$O"򸒑~!U+糛$sf,/

qvHղ]Vٽ}H
uqS^*'TRƟgŗmʸ>zUUD4TYҰ>&SU+
<B\*#Чe+"ͦg5	X{OX5r !gy"x>Ohy ydpF'48kjpϋm4<@F\7bu||YUE
-V
tlQEgQN>a䅣0d&B~c`7YO)*2tA!}dRTF2ilHQcō
\:ZuSJ)|}lZ@9ZjQ5x,OMJQo~'$kNҍh_-|1D6!ϧ3g?x:t lSP8zZe$vO gUޙnG9*
!nAo(6E4)54֓վM!nCn	!l!BC~DNU4C$Qu'u72cƟ{$3:osB'|t'JUQ$RA8_yz,)%kI *rn ?3	MffÇ=@
S/5TE	O`۱ÃmQ[;pC`&-@"?Afg
c0"3!
1k:ǣ;&=wZE剠yNQyA=m_ 26h*iP}^l+[}QV|q*LKUuO~3Q}{2UQт;%V<cky҆00G!l4Y^Op/4I&Oqv'G &Bː⼞˪)Y@%*4d%6O}Clo\z	JXL"dPKNY{N)Bo?&WSVR ㌄=FHqX`t%>H%6TS@Tyi/k(I},bl7V(u,]t.{4i`夋)[dKX#ls%qZa<ѻ:ICNf:ԟ;qtз%շH=PJ?l&xKDjR ȾxO}Ta{'MjkQY<9YY>Ic5
k2̑'LX#S *LpUf?vPc)nęe6O v]MV kiԂza@ v6.ZSX/x}bZұ+]'
yMۡlhkfu\ɭǉ^EKdNae
@f!UvEDz_ɣ蒿m"ԹHme.\QteK+5W5v [-SU
ܝ2p5#f~<Ώ
3}xݝ~XV)83`M);uQ|m/A/ȈNbf5W'I?6/mgZl¨1>n0y+)t/od^$]y
1
\"D@ak;SstN@f&.y9Nji~#vdo,tbhfREdDdY)ܐt`l)a8NV*:);v
Ce!h:,¸XM+˦ J
<B3j*Nx:w?=L\iB89U[w0cH:V)s/%c.t&SjY$Gbd͊Ȇn~
/*
qՇZ3>(ͤHb
xV
 _%!J=ӁN+yB{BX~'OO,ſJ_2 xң͕_zڑ&GLEo)>n37ҜHwj7?\L9&uҵ?cE²˚֜]Θ"D%OL>,PMMtJnWno޻n%JGo;˨Q&b/T"2y8_{whCOkCY95-:{传$iUt
=+-3v
zs[T%Lu@ôrFnGدE[GhS\%Hh堸*z-M-?s|V5w\b&
Š^ZNzuK,*j*;q^QĜ+<ozwӵ:Bڑ{н̻~[Gz=սjC>LG/.B4) BbDF"EG]fWN04p!iѾea,/r
&DIY
~Jnu%+MɌ^@MLuOnǋ*]y,HFE'd;j<hz09)T&6orP5ؤu%r/;<<t(9M]v9GɋE,TAo]ƥƣ}Ohn Z/qcSMw5VH/#C?[~NX*(.ȁ|GC>pޔoqfn~ŊM2jg~-5$M[d}C.yϓg2B0pĬYdV¤fAKF3"[MEKk<]$Bmg^sӠde


[[FILE_START: .git/objects/96/de789a79c503b778df2033a3a1aa40ed9143cb]]
File: .git/objects/96/de789a79c503b778df2033a3a1aa40ed9143cb
Language: Unknown
Size: 3,072 bytes | Tokens: 1,453
----------------------------------------
xZn:g>\%-`|О M^KD;jdICI<A}$uK;e$7f3boϳyXLL*'b+dIl11ɲU)~<sϹUEX^L.gi^]acqh2Pk,
b4C9WiY/8N\g?}8~	?|AK/ĞjWtZ%
Pɬԓj%B`A~?Gj]^8Pv0 ^YgR]*KFl[GMzrGgfqන(KR!`<IVB}kVs-+$U,P\J;Vz	06󐹘lbͯ&4ySLCW8u\%庱r?Z94*rbt4X7/C'`VWZLYs) "%2Uqu0+<dqc24$@d.5TKZE(
jmhe:hiWgN5JeeR}<RZ\
-vMδY׋;5:Y]?Uk׷g7Qd7nƋκA΀Ɗ;~޲["t܁Ѷ(cA0^[$j~^IVq$u&F`cll|ٟåwncp瓏4uy!aSXxH:;
ղ}`0@1ec۽<C,A{:
lN0Dhu]ɓ
a2ʚ<3Xa+vR&3zs1 OV@SÇ]-
ɶG$
g&@#M5K^Km@kMpg/N};l ARua?1;&&ޑ%LJyghb, ]Xy2FkǢN{أ.ZIni\y=_Ct%X
쑔l1?$k04AC1z{Qh;8tow@xQfޘ<nL,fapQ[|a$:[ < X	)%HߋTbXGat!I?l0V
# ْ <MXJTW	'T+d@t,쾅CaV@F @!ɤHe2`}~ cW՜$9;Ls,gIfCǇì$4Ɓh߻~qҋ]#xBfG/u0At}n8Vd8nG5ƭ3t42Ȓ(L5R@Ƌ*!@]ޘxwdj^ޝOO>R*}Ck,GE63)ȸO8JW' 6dn.&~=&gò$;c8*O=6H%^g=*su
4$ʝyHiv]"+|4.:CzۀmVCh("q0Z{q̈́.tRv4:B'Awڲd/QR9B;f8y
B
0)fSCsƨ(glddjf=ET4oXsDb5ź:"z譾GqŸNi6(Q7ٹvw5mff-8FmJ(2vuِ`f蔉Ǜm
]ϒ(hb?r9h&m'<|"	:iL#Oú,R7}QEgrn
_Jndv'R67ŅnIs?>NZUomA!K-YURe*>hη%?751xOᓈVeeZˊT69%$SYωl·}QM>jϙ'`lThvj䙊K6ԁf.moVk``ZuvOnU7ZOCz
\ot_АUUaUIO
e:T辽	pf;\m<9@nS5xnEP(jܑU_$
'@(@&#ޣ/k%hˍY:Ԭ7PdڝΦm{O}_QvkY9srS0돍3a3Z:f[4um~
')LpyRw6Jx$2<_eN9B<v|IVkx(X7#pzڰP
גfrV{GKdnv/ŅN,bQE<vbMpg^0nDD0r}lZ2X/PkkgiL^))_ei]@B{ȪF_RwFTP 
5a޶5G)2CU#m#6 1Q|Y0drL=JxoDM&Žѡ0<x|Wz&+P/=>in]~G*+%޺ o[U2ʋs%$rK,gyl\g7$+9{s;vλ5ԫWQ_Xm٧//Xys#	4REs'^}yC6c+")s -O'VfiUuo4/x:)G('<Fx0NSkn
Ȑٷ?'yz?SY&hHy9LN)x65\oKsZhP4tӫ%Q_w쓭3'Cqy(


[[FILE_START: .git/objects/ab/b960b5a8c8befbdb30c96fdb47449e6eb94a3f]]
File: .git/objects/ab/b960b5a8c8befbdb30c96fdb47449e6eb94a3f
Language: Unknown
Size: 3,132 bytes | Tokens: 1,568
----------------------------------------
xZOH-`x!]б:6!	ZJYq׺<6~ꗻ=3hOcwWWU׻gZ6SO+$kĆyQ%S}_YӶkf\8heQyYTn]&C!7]S62Czw&!,>;u
ǼĭxC/۬\Hzsޥ{	hbfmMi,kl]D2f7]׹%`lldm!NSb1M'4̚z^\EK_^^'Go/EX.;b[{ַeL 雳G
M#h)+ᒞ',xۼ B/^9>9J
{^|x{6I@=+y_I/.N~˳_N3ugKO./K})l^||},:3l?>|-vTFtYhL6@Rl*#is{p\e2g%j}j936e*
BL)+DMϛ\VI	^15
nOɻX9Wg)jM1wA-	`;Rq3Ok-S%"ݣ~uHJvP;o%;R_ES/ci3dE_[u0~ǡŅՊ
8$ZE*jɻD"`_($Pܖt]\f4@7u<ԅ"y &*b, %YgUt~2ͼ^uluɎ_32O(kZebW:qoiCBv1	{IR?+|e5i	咇=Y/^D3;, h@	(]moќ	>"]H(ǎ8B~ڽV,Pe,B^hSğ7y5><m:KFo~A*~p`=yѷ_sKd|J
HAP'e8hɡ*8X*V҇@VZsz lDq$s)䢟}Wt
0pC_r)mDǋGD2{	=aOxF'xA*)=-tt}+!P9#lxC,7.,ky#Q<HSJMFz%ꈼeP=b7d0Ӝ9d4ho}	j/O;~`|VNbZ((ysQMa* "c0dg{͑e!A>\09-nre
q807Gn4,0]'-*iX9YJ	Lѐ^KP׸n#(ǈsJYq@HT$)H;9xB}ѿ=#ЕVMNE4aVIzNT/?e2Er"l:jū:@	eZZaq!:P2Z-ӤyjWgjV.f]j}\ԋ
:''Oby4P*3Re>ڦR;!˲R*W:%Aݴr`DO_b> !q>UdV{'N=!C`Vng9a#ѡfMUQM	@r9YE+N"F4+e6-aqZ$Fmjp:ȃiQO%C9HSHQ> t5b=S!	!m+)D:0#unQA,]V\;;],
þJgD-Kh8!<樍yǆd8rz甦*C&W^L6rgbX>51Rf'Ǟ9*ZA2ÁP
W+`Juh{9Lu $QkpN֗C{kjQp]"V:R8\z;{X@v`y=k9z9W`02ZlPve1BHf(l'5['XSh%&HѕZ
jo A1 <} ,A$҃!&CДtU9vc@#
00t/س>t;Anޏ@~
r
ZC6\?~|B-$HM߾Azzv6'ofe+W]G3"/"ޑ,v2)JWeȡkpgIȺpHL5v"uѱe7dZ0F̓=zI h4N݇1hsHz2chla+i&e6[TiQXj0`0T1ij6777G[9nf*uPj
z9[CQe4kF,Ya47'2r_{zPJv6K[-{5+PPQ9TbR;
=TEk+L/s6A[8`VF$쎟vW!/- 
O5՗zW{쇌jol
AĀgtXg,+*y,(}G {ٺ%`UXacCP¯{ѳ6Ud$?FO@n&adp\|#%_"ȬT_07&H] yHjdړ:Khn/mb?aN(̵Xg)JI7| #Pظ\y\n<ڑ7 }M4g?KKvYkB^ ʄq`,>8l)-Yb
flZ$6£BM{uD10;Ԉ->T
P]2Í	ulZ}O`Ї{sjvaNeM*+45wJFh
|ߘ:oy&р~w@ A*


[[FILE_START: repo2file/.gitignore]]
File: repo2file/.gitignore
Language: Unknown
Size: 3,139 bytes | Tokens: 50
----------------------------------------
[Error reading file: GitInsight.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/objects/c8/93ee571d54a0df6d0bcfd3da04890d747b9132]]
File: .git/objects/c8/93ee571d54a0df6d0bcfd3da04890d747b9132
Language: Unknown
Size: 3,172 bytes | Tokens: 1,646
----------------------------------------
xZOH-`x!=ݡculB:JYq׺<6~ꗻ=3@h'R՞͔ϗ)$kĆyQ%S}_YӶkf\8heQyYTn]&}!7]S62Czw7:!,>;u
ǼčxC/۬\Hzsޥ{	hbfmMi,kl]D2f7]׹%hlldm!NSb1M'4̚z^\_FM_\\G'o/EWX.+Tö0Veo&˙(~Ogǧ7ǯF$$sSԱWr%=EOYyA"L5b,x(=;4xuT3"N&}&Z>~8<>l:39:Nivu1>_~'Rv23G:(%Yu1g
}y/a/[L	pl08# Uv1.bG빢˾eJL7r>g=m<U&?)Rӟ'jzt*DFMJ84	?-&n+cR<b[!6v,"Jv'gww"[4}6JD'-9"*q>BH)zK!ڪ[+.\Vm(A$Yl<*BUQKf%{B!<J綤&2y缹	ߤ.X5YTuUwg (YȪ$_И<>+.M..ӏѕo--`edM5#B]&!v9)dS/iCJGroLF;-8\P9eKht
(A4+qycB"Qcmw33G 	cܑxu#RȿWJEQ-4b
&ﺦg'A'xͯH/wwn]ң'ϡ~ kn@RwvI@O_!vZ)Qd,'-9T}ACEJXoΒX"-W0@Q->q0dׅ\ӴbRAY.}PZΞ]?=(T"t~숒Hu/'@ψ/UeS#/] 8E2Nc%*?g
vټ֑XKm6ZjmT&Ҕj<^ee3}:"e`<TX74gA$
g_xӎ{7
?
+C-r'eASyu  /Y1^sd٪~mH-GDgż[\YC+7Nn4=Ǎ<
3K1LEWh˂JkVNp,A4$גD25[ mA0l1RV>Ur4IҎ'`h P=Gա+d?Pi4|[
-eDجu{WQՊW1b':CumB;BNүã|CRud$nD;ӧ͵ZIծΒ>L?n\R"?a!aV٢#<#vKJ̺'4l14-}
#[0ϕzKeJql_TǇjYVJJsV6NadvaQLh.1Kmp2~?!FHj^#(8lT0T!*A6Utt$b_~UfKǺEIۦ.h^)r~ TRal3]*`OJPrȰnHۨ1FtVu~@TD.:;hİo8:ƱC! 'ղbX
q	(L81G
;6df&> aǹ
c`T`p8T@%y3:\I-T*F{Bc WR xÁW+JuYhչLu@2 $QkN֗CU~kjpl,?|9zxwwjԱ#\zE}}r=桱[lUJZ{eDM$Q Nz	j! r;KM7E?#{CQm%@#H# |#pD\PS'!d~H;*] ux#a`9F.=S̈́={Cg8GcX^jVSǶ^ԟju]Rjҭ
g&ԃ?i~7+\R?)\%LDVظ/C:X@<K
@}gѷW+!Wח1y̼@0lM+"F3}6G -s/=
l2fRfEYVU090C6
~m#|ss/p7(l	Y~R
֠>UQfhAD8EUbWgᶏMGi,Xǒ> Z1wƇZӡ&o4F>*k]!wf5})uQe
ڢA8*6$awr]
T}{.Վ~Ȩv͖ذx@?0J!oK/K5z"JaѾ␇I߈^ 8QVPe6v~jQroGI =+Yo]UsU&Ô8	B.Hɗo(H62+QJx2m6I1RA@&E-ǻ6:*ƄfO;^4Jum66VYs1ҍC=6.Wlq݌7A/\J҈CRj0.Òs'.!-2a\~[JtKxWqgٴy!Hl8в_Q umG10;Ԉm>wR(	oqCpcb-K|Xg'LRvaN#8Uʦiuk%#4r>Mh<vрF<AXT


[[FILE_START: .git/objects/b9/7e692890cff0442664e02b3d77c845c4906e8f]]
File: .git/objects/b9/7e692890cff0442664e02b3d77c845c4906e8f
Language: Unknown
Size: 3,315 bytes | Tokens: 1,649
----------------------------------------
xZmoܸg
vAVi-P'qp +WNbDjwWn9}͜bjNF'%eQr;EnE?of^Ee?rg5k3*93]UOg&Ey}S΀QXoeuIuλh/$X>1iesZ#ZX/y'̳mun7zF>;;Y۲#hӔHL)&^?_JN޿z`w3b쇗XߖM3Q\/Ώ_o^\*4Hɧc+Kz΋.mXj"
I<8$86x	m\1`,N#U[	CF*_"?''bds4:%>]]N$ubN~|uIJ
tc;_+aQ9O䃄첓Z0R˺Gk' bDTǸ}[ϞOj\-QЧf%3iS`z)9>7IxM \+j8ܤ7d]my;jMtA[S1,<JN{f뀭SM'G1"*q>l,y+ىS4:6Cԁ>\9䯨p^!dyBXpUE-y9+8:
	T:%4yY5ϳC6lAgΛ:BMBX<AI
؈u8Š@JV%BaYqjrqt]n4~3owe:Y@d\5-2	+M!{AR=)|f5h	嚅~^Tf8e<[&"p%o"2LH$j,Խ]6RrFs@w" pL}s$@AHF@(
iFWL2]tC6ytp<Pb6
^tjI??_rKIK
l5 E7\!pќCdq:lQ$"~
Y0Iw6q0\PcRNi}蛐[N]?>(T xy6%[ڽ?XC'?/x*!=-:I(\6<ǡAy=űiB
{lp<F{LI%&yDʒ:!e`<jɛj3 _xק
?P>bK1o+m~VyQ:Mea "PdfG.{e.A>\0/es@8b7nh3Gf4̬0$-Jjh9i
	Tސ^sPn#HBǈr
Yq@Hd4)p;9xB迦jrJ}GioϱWUX!Gm!(U$#a<#8򪖽ƈsMס	J6Z7~~^{IdnD'V)$ebWv
Qw[.	ð鐃stEJ%]e2
GUE/6K{hU۟.;s%R9<aZB,/~Z1M<w3yXTo8~װ6h8#lPtmv(8lT%Pd!*@6]TTU]wb1	@*y%d|񈲮EkuyXi{%F%=~W')ekL:
sU\)P
i5ʈΊ@҂Ӡ^'﷙	=B`D{`	u0(G߳1X.9ղ6zTR7 5;$aϨ錉=y"rԇpG'"UМp{^>Ya0ZMIYOs+䐂(}Ԭ⸨EkliJ1Lnex:2ܸ?u(
V>tGDIwZ/Aap`
UD *
7f?+FuRsbZ=C>(,8ICqkqsCm;
lqE5C=:hD\頰^4yQE\3BSev#D.7CQ1;$r%(l`'IthԸْ9&/HӡuTui  4p`v6P
Q1IG& O"a`9ؽFΉ=Sr3{CG}?	뗰8-XOA{kQ#OG6Lׇ+lgc.oV2e/r	T]f>[JuWewkIȺP5bx:xTGn_[z<ܰUB-A4qk؞(-=h{g$殚C42[*@БwWQ{m5o;/k0(]-h~B
%֠>UQf)Pُ
s%cvn$PF
Cԃݞhkّ+A4+P">dЃ?R
4](hY!f7}9ԭ 
:@şZu'{r[&FR̑ؐ$@?J*?M]YC3Q.y,(3
A_.<cb]1ft7q}0裿/wL%\	XjtG7A#|Ce.
Ff#``#uaP,}{hO\@sG~Yo݌	{xF,ofj?Jy&Fw|C"岗i{u$,DFJ$.^\*K9[;e{^5dF7Q*[AXg(|>q?;8em'xZY[PS3~퐺ujZKWcjVb+$NgqE].Pcz%b+I|Ah'ឦB|rNk?ʦiuKzxA^x%5PxNt9IRX{:b`<d+)gfFCJ(B|ߚĒ`YwGf?o^


[[FILE_START: .git/hooks/update.sample]]
File: .git/hooks/update.sample
Language: Unknown
Size: 3,650 bytes | Tokens: 1,106
----------------------------------------
#!/bin/sh
#
# An example hook script to block unannotated tags from entering.
# Called by "git receive-pack" with arguments: refname sha1-old sha1-new
#
# To enable this hook, rename this file to "update".
#
# Config
# ------
# hooks.allowunannotated
#   This boolean sets whether unannotated tags will be allowed into the
#   repository.  By default they won't be.
# hooks.allowdeletetag
#   This boolean sets whether deleting tags will be allowed in the
#   repository.  By default they won't be.
# hooks.allowmodifytag
#   This boolean sets whether a tag may be modified after creation. By default
#   it won't be.
# hooks.allowdeletebranch
#   This boolean sets whether deleting branches will be allowed in the
#   repository.  By default they won't be.
# hooks.denycreatebranch
#   This boolean sets whether remotely creating branches will be denied
#   in the repository.  By default this is allowed.
#

# --- Command line
refname="$1"
oldrev="$2"
newrev="$3"

# --- Safety check
if [ -z "$GIT_DIR" ]; then
	echo "Don't run this script from the command line." >&2
	echo " (if you want, you could supply GIT_DIR then run" >&2
	echo "  $0 <ref> <oldrev> <newrev>)" >&2
	exit 1
fi

if [ -z "$refname" -o -z "$oldrev" -o -z "$newrev" ]; then
	echo "usage: $0 <ref> <oldrev> <newrev>" >&2
	exit 1
fi

# --- Config
allowunannotated=$(git config --type=bool hooks.allowunannotated)
allowdeletebranch=$(git config --type=bool hooks.allowdeletebranch)
denycreatebranch=$(git config --type=bool hooks.denycreatebranch)
allowdeletetag=$(git config --type=bool hooks.allowdeletetag)
allowmodifytag=$(git config --type=bool hooks.allowmodifytag)

# check for no description
projectdesc=$(sed -e '1q' "$GIT_DIR/description")
case "$projectdesc" in
"Unnamed repository"* | "")
	echo "*** Project description file hasn't been set" >&2
	exit 1
	;;
esac

# --- Check types
# if $newrev is 0000...0000, it's a commit to delete a ref.
zero=$(git hash-object --stdin </dev/null | tr '[0-9a-f]' '0')
if [ "$newrev" = "$zero" ]; then
	newrev_type=delete
else
	newrev_type=$(git cat-file -t $newrev)
fi

case "$refname","$newrev_type" in
	refs/tags/*,commit)
		# un-annotated tag
		short_refname=${refname##refs/tags/}
		if [ "$allowunannotated" != "true" ]; then
			echo "*** The un-annotated tag, $short_refname, is not allowed in this repository" >&2
			echo "*** Use 'git tag [ -a | -s ]' for tags you want to propagate." >&2
			exit 1
		fi
		;;
	refs/tags/*,delete)
		# delete tag
		if [ "$allowdeletetag" != "true" ]; then
			echo "*** Deleting a tag is not allowed in this repository" >&2
			exit 1
		fi
		;;
	refs/tags/*,tag)
		# annotated tag
		if [ "$allowmodifytag" != "true" ] && git rev-parse $refname > /dev/null 2>&1
		then
			echo "*** Tag '$refname' already exists." >&2
			echo "*** Modifying a tag is not allowed in this repository." >&2
			exit 1
		fi
		;;
	refs/heads/*,commit)
		# branch
		if [ "$oldrev" = "$zero" -a "$denycreatebranch" = "true" ]; then
			echo "*** Creating a branch is not allowed in this repository" >&2
			exit 1
		fi
		;;
	refs/heads/*,delete)
		# delete branch
		if [ "$allowdeletebranch" != "true" ]; then
			echo "*** Deleting a branch is not allowed in this repository" >&2
			exit 1
		fi
		;;
	refs/remotes/*,commit)
		# tracking branch
		;;
	refs/remotes/*,delete)
		# delete tracking branch
		if [ "$allowdeletebranch" != "true" ]; then
			echo "*** Deleting a tracking branch is not allowed in this repository" >&2
			exit 1
		fi
		;;
	*)
		# Anything else (is there anything else?)
		echo "*** Update hook: unknown type of update to ref $refname of type $newrev_type" >&2
		exit 1
		;;
esac

# --- Finished
exit 0



[[FILE_START: .git/objects/5a/cf850b9c11ebcec2e50490c190219b8a1478ee]]
File: .git/objects/5a/cf850b9c11ebcec2e50490c190219b8a1478ee
Language: Unknown
Size: 3,687 bytes | Tokens: 1,825
----------------------------------------
xZ[SFg~E8`,}\*5V-c9}QK3a4sw/j!o;W7L,F4^,BRT^ЪeSĲH{iŏE'&/)v
̗SdGo|O6/d5JO=rU3<HuC]uyf=!Ҹ뤽/EzvY+s%ovԹ̆~"8)⺑<dggOe~5IW`4$/ER;^_į/ON RVehydKYބrbas&<0>|&e4Yp4jQ n,Ƭ8L{u:Ԡ\%M!{YXI<$qwE$5nFb>E
#ZdcZuUzE\4i5U07^d{_ej~\^\&;\8Ơk"ۥ<S	ď7yS0jyAB,QCKpvWU&wĮ5Yۿg9j[wy{-bxoZ_ZwJ6.S!S{Tl]$J~2e
:ZiUl;mawWB-K/߆뫚<:qXK
m` ?]Y5$)%$2ng/5YZ:yE! w!l_1#		b͗Z^5NȶkJ.ρl?T_4p	^8
D
(HOk`?t~%iyƀ[4$F"&8z܏1 ΅jXD^pJ 1l$1q^
Z<"reݵ1% *{CB̠Wdczz^[O		
 Lܽ޹v~h׷w6$=Z
k z, qLRN+C&2%HxYIn:ka{ >iRÅde͑}*Z5Aߥ:(|ʏ[*)
J*%P~;/	l%m%wO )y֋̧ݲ Wutv/tkP_
odW`IQL_^go2p 4Q2d}[M&"g$VGΪSO>HPD~-]{0]|M
M'V8e)5GS`Xi XZu!#CˀJqOH2K)%Ӫko7B9.*R)b0;(j0(l	Ϟ
*1,kd±7Ovu8=Zݶ3
B{yXڭʚ3Һ=qklb.)&oY4v9(lI@ tGvC0EAD@m
(~2P6OHTz*Xvzv娭$QR3M
G8p7w&'˙#wXllESFϠEF鍞[YVHzH~ĜM[*Q
@'3]>T-|Y\v~zYfet3Cةۡ^
2 3TpEk6ӐlWxZ7DA3a>)K)!E[@[/ rkGCkbA2
iDbv@:Vfs?g39jh $]`=y:jt3hIY4\пxM,"
Ba?^iLU=P}1ak
TjCƬeeFb5԰i=P!vT+xd7lb+u^'K.IӖ8B_s
7d>.!$DF?qb`}A?~ӚoigxtQ:K61LL<m4P'MT<ZH2v<Ƙ=-pBJZO&ON(aN<$P]JFF}`u0EiՀQ%IȘ7Y2IdhV=4RO?a~LͩMO00;1@Jxf'j{?4S̉``̪uJ!GEgnRK
's*(eAmUDn6AdyNJI?xf(?1C⅞Fd,×\*LSm~6quY	
{2L,-dRvsVvrz~zsjgfC@o1Wh6l.AD%?oc?`rFf
YZfnN͋,c$GR*0'fp/gh_mv%Pټ99OFt3Q Xmt0#ꖒ(^YҔ4CsdcĜ:1A=GYDm﷠5P69woD3!T*(ۖ1x\c܃
;pX}T+R	i7"1(߃z0(51P=`lFPwd3ˢQ͵gΆx1/mla>,;wm5e!0IaOOpL8r^5աymO՟+X-C1x&%BcM3DJ
3$t?(Pҥ.qFç#s¤mpQE
OrRi	ϟ+UotU0N4*5$A}ė*G\zF5HQ:0$۳-}  ߂\
k5)
#61<!GO;!-*Iٷ\*Cw8Ja@	ˤKE|@EyU_	~eaZێGOyИFсAHtA
.ZtQ>м:NE7s}sH[a_־;l%-lB/̃PN/a3`$b !&PF[t7!*M{́4tveQR:x)_ f||iтj
Dna]_ nȬ9Y/ܜ53ὈEb/Yix3[tO
#{~ppBVDLJ1
Bkֆ#FEhY_m
%bmwa4k)eOn*]Up|f'sK_;XGoR+DwON& 7|bz:.wpqa|4(7
@nSwO=m>!h\%BQhӤwObh7\	x(z|O k597pk&q)xzed}Rm4l=FyVÍ{g:fRcڋo~tGi`}&Zdؽ:"


[[FILE_START: .git/objects/ba/29d0b7017f2fe0a0af0fbca3fe8b739a209406]]
File: .git/objects/ba/29d0b7017f2fe0a0af0fbca3fe8b739a209406
Language: Unknown
Size: 3,852 bytes | Tokens: 1,890
----------------------------------------
xZ[s6g
T~4#Nv;κ4OC͆"qS)MgڇՃD߀eV,Փ'F+uzZRzS<]VuUgbVYT}PzS>kLzUmt_"OWSU<		,_us3o4JMeZ\Tok<;jC7i=W콉,]M/MS*%QrM /
CSՔY)*0xI0988Tϋ|4eTEdu*l~8{"|;/9R:5O*hw/ӫ.'(O2	NPFGˊCLN&A{4|sLvuT~aM]]e0Jdu{&vjY^`TɊ(f.Vuu qҭ=횚aaqU6/ϼ,Z#kEZ׷ER-WAW2TɉHvaeV
UZ,ōTi]2M'Ero%ѺHD&MadtMfߤmay\s[כȼtyDsM:To	VPŲ2Bx0.Zu5zm%b'`tK~srGawXodaL&/J2:d
Y&l3C(]pKqDT~3rYLUEMg_OUEz	@Z^6 MgD9G߬FO@q<x̰KG:GOlTAiMN"5|F@HpfM>ȓv:]V=I>@jr7 ҕʋZ&2~J
v.$?,>#P?^ ?пnq}(Q!/F~JK|g(K?	a?jrT^hi_ PAzίgI8\υI.*I 1^w|Жs,jqKMSt""hC|:5?՞ Za wt,(ھ	-0hb<l
=<rv\뙄{e`sXVƄ&V*hҡDnym٣SVϣ,ӉcgPUJA{y+x>Gj蜉UΨ1ZeQ.ĥv;aoUvE|gM@sZR	+%*Y7UnZUH	rP]r`Kjlb=YKnES`IAiVYRTVcٰs/=,P̆H)1#K5
[[;7^; DLDvc8/`	supEʺl-3]-Ӽd)"I_ݲo
Uywܽ ?NXpfB@ǸQ;TMc
WOwIo.Ps5Y8h컁
~v.00@"82TjLQXyaÙ@@:?Tϴ@z
텲β[Ĩ(1p,$՜nYs힇ꕮz)nڷ&A`D:>3k?2h75=9zZz |XfZz.\B/j?ofTy	bZibYqJcGl;BBЎfCr%φK
+Mq[mjC[ eQ
!Br\6H
"Be Ϝ+ f3C?̟GLߢe[p'47 7An` i]mFva{mn;Ce"ː~+rzɂMg$4;84n>;Shy$d'zP}q~$yGM봺]pnď$'?s~y8\a^b	d}yyz,Ĺ!>78~W+ZLNhm_h_X0PItb/v^%1i'J]6mP$ŀ.ؑ t
<Ox-{h
y赦qWo~]bA#31OӾBˉ
/,bRD
!eyq7Ӫ@᲎j'-Sڇ8ZHP51
\mu0 , c0*-^!~'R6lֆu>OB'ԯk:kniENЇ|a:sGsUkTUkATg1ã1!(C9u,LwEyeQ7lK%-H^`f{TZ86"yxg?/:3]l _ve{96§Q]GG%/ӊbՅs4W8QlӲggWg.[{T9D	5u#ikk3iS2V<Oss=/(
eԌ-xK?W
x UZE׶s7wja)_ۂ=ǡc(HKg].y"GG$/֜Di1;8L@8Z8oA.~\AqJQ̹JL*A#A.[u6#up.h!l7]Zyx,Ke	]QaAK=~zFD;%.,K$e
=N|DP
NgdWn-Epgrx'3VoeZ]Wobo5`-N5y*j] ueS*tU2- zr 1m0bGRLen&}\u
}\73QheU
􈮞}J"F 	8 -=z}RD!o@ejrQ6үe\(Z2^fcHXn !|v*`W<ɭ2Ɉh(~43d9alC?^7$.0=u6	G̏+ty5$_d&ը(>|]
:
4'0u}7RV#d_iyrŞEp,= c9<Jd={[=O][EK4YG-L~g뛁:,
g.o
/;,|5.b>sHQV\bU^ amn˜LsVd9?c[.9qBS:/۴Jqf۞?޹٩wdXpE-">3Ժ&m5=D2'fJ_.M#ݒF,X4eRڹB2v2
7 q:*ƫly1!^-]J8gI,]k]
ֻnDx54͕[WF _y0p󡼕."o-E	 :t?=H^s>uaS7,'C-=]7Fjdָ)=-td1T;Ch|$PגW?dz}qAíOAf


[[FILE_START: .git/objects/48/90233a4d9a92774a14a44f64731c6cae9f1d12]]
File: .git/objects/48/90233a4d9a92774a14a44f64731c6cae9f1d12
Language: Unknown
Size: 3,870 bytes | Tokens: 1,913
----------------------------------------
x[n<,Ttצݦ@6n$$u(r$qC*/VAWѧ3rHJV]͙s$&oC6*HDYLY:gUqSQog7.:;OģAأpO yXCΫSq^BDE)S{WY,"
vŴJC7>xH"P𳒵&eZ%J#Ȱ$>&e:ELA;%r?ALZ΃s'4]V&T%݅J0.,."OdBTHRwR.xf<$i1MxR<"c]eIҰ.*)`[H%ұȶE1ti$ɂHoҩtyyUwnn%̳Pr 5 @i<x6K)J8q qdwЀ.
9L2l
Хf;A\([;p`.,?n3Q\1\12& $TJ)lCaD"= pZ%
.jIZ
0?Я@E*F6hdY
ғyd_rOW)$$>zG,
9ARH%"$XQUwR,t=ȯ[}=?tѻEtkwmk$?L"`Ga|=(ekO7앱k]fN.(y4-;lCܺ	!!5BA>&Xe87X>q=TӆㇾȘ'FT4Ɍ.s@'|T'eǓuFAIC~% }% ~ߎ$Ϥ'2W;[tóͳV,3>HDv8]ճj#3 ~	g!o`녬Oވ^\6<P	/k;ʃHPe kyF5m? (3s6`*Q},P44u]SbÑ=-eiG~Q<"Z_5̸7/&7묶ujKZFoCl)19_.U`#<c<kwҧx8-2cjPQ"uǯJ3Z`sq$%aR4,&'2sYvD.*OE!u~4b(bL5Nݨ8aԐ
I8.3(}0葌Sn6TZҍ]	^`-Tx"N#ym%OK 1øRi|ΣK5ŀ~݋AhZjh_ȖzئŖaM䡚aOάR;h)GmXLWRIВFpekA%P52]S) ȮxHKJ3NvI˥LyDl)-VV)=imĭkk;TH4ҕ`	l/ij ilDIK,0VgU!xΡМne]tKyιN]Z {*sQI6|ޙqߤ-
lˆ&(GJʕ8я&J-<dߏE4D1P&cf*H*_x;ͪy.<.:BZ-+fjVM+PZI;1^am%r*nŕ/	,mi	>t{~na^wcpomy=zo^t%Ц^|	Ac4=ʹ*. 9ϊ*'Y[!Q#=7x#k"N.dzHf*qݾ:-}[k{Ln >Áj".ޜuuB)Z!T#cۛF]5s*#R.Y$䚤
f-Vj!LJe@*<|t=e,f!bNuِ0v¢:]V9pz{js;9>WrZBYS#k
o/50ޜGdc5lV"B,z,_ƃ]G7ɢօS(=FsAgmPIAYkNY)l\*m\D>_rBkQ{ϟX&Gd<Q׊+_
Wjn@3AHqJt!`_^󩾕ѧ?p=Q®5eeW鲌` MkL&8sw۱:uyL.T'e >i.Nu"&*Tr 5Ao*D ٴ,drwnjVDp VAZfq	0XGUo=<QO6O/gOCPF=|?]+H8ѤwFo,xB$,#ﻝ[q~pt1Ldg+${M` 	 "_BAr<|ʑ><G +|pȌEV_c1Z`8WЮk{֋b]\']ou$bRg)k4頒;X9n'BTwU}a(˪{/xRdP>:T#5"tU2=.Nz^/u.܁ܵVtmrrXffoBtA"Gә%,ʩh!DaRK{Ag-_p	Pw0bir5qMQi~GLCrJ访ũ7_];NS\_|	J(ܢ112ZQ`K$rKCӞ05Ƈ8?|&6Ļնk3D+;kBF|!R0WwhUXdy)_XdY9l̸؆KگU57T
ErMJmVcLw;؎6;]"کZ-޳jz<S={j{`{u/}C'Nd>u4:' -Р!1Rŝ^rxad}o0h='~n:)uա,Oq*!c)C=,.rij--QOVAcbHto 67~Y^i*MDmGqv[^SF]|%#Ai'\^m%FkUa]إpug9'^N2<(x⡚u=t6.r鬸c(l9QԊ> Y	q$*]&_'m zeMOeO)aWT4"I٘FУoCf7`:,N'I:$&r	6þΑQ3`qCs"G&.JDMjz{7{w0x:8ޙumY{;Кr
۶/5ͥvnҞE
l'W8?
涑rodNr0. 3B5Ħy@Уv떣
m<>q~kҪ(HU
-S[K ɖaK.7F[K#ehbELMy%.5xz9E{wyO~t


[[FILE_START: .git/objects/b2/cec8adba13417fac04cf01cd5504bef2576137]]
File: .git/objects/b2/cec8adba13417fac04cf01cd5504bef2576137
Language: Unknown
Size: 4,196 bytes | Tokens: 2,077
----------------------------------------
x[n<,Tt7.6	|ƍ%$n(R%);^@ߠSy
Ιgx"-* $ۜ9|,|f4oZE('EI6<&UUIo^_~y||q鳗>~ ɞFvO yPC=1;q>Y-dVQ^qRV2E08xygPQ,=1]e)7w^xJ"Pg%k_K+Y\TNM`j8>f
:ؑ|>ȗ\3Yi9```|iʣl֡Z6.n*ES!ήHBV1Yr.'uq}J"*<ފiTGmK4ViUDҰ4NeU/=lZ@F.HT:Hr:>eOdY/	PC)" 4p$ф)
v88ECǉ44OC~2e|
Ч1ɗA|8HKp0_E^`7\+AL~Z

!44L8+G/r@LaWf06Le%&@i`b,:[J>Ւ4+cA2D4O[}#ۈ @4NmHydW$LEP͓2PXI^6ZrNJT'e4NG*V
pض~+$ӕVuf--o.C]?Nۺ}wwhCX;&)4*K?B.KIK[ӵR6tNfv/m͢ϣiQm%YeۄH/6mM?;:|
E+E;ejD8QLVel8!tQR71;ʣGb0$KMPcQPT``~dx`o6qɜ WB QMTHLR6[+d nEF锒5;:)vj>$2.1zZ~n-4ΎxZg?r)b9 jG~\FP"2/G=ek#v\6:¶_݁,*
PBTd`d =v|dF4톊@ ̕$ᣵڭ"*E!p[rT-^JiUad-IqG2Vd(AՙS}Jd_ae
%uTZ=khY4@D$Vika` 6b 15|ǚh!EvIu o1EBF?S]RK{WISkf"6epT*1@O~3k͔2)NaYKe4Ay4V_f]kT[RKuRXcm6r,]nG0/U;AS/Cwǳr*:(nW!+P!K<j[):.q.=k$	
XL"Le6BV"b ́nQDb(bLUXq¨!I8͒gg'T9u{= RecI7k.[S{"b7G\	fv$䲙G
k*};L@Y4Ijhɖ:fa
}4L:$fzT\QBS?ӗT}=$	JT&k&Zo*2`'8Ƀ`4x_i&)N2ɴhY?OҘm6*=I9F:'ߡ*@B9+LpVf;E˥]!OkWqd	 kYORVM*	
7ǺpR\͓ɜĤԅR2*Il/4in۲q-5~?J+}7V^Q	Ue12	>#SoUQ7h8:]0y$]>BwZ-+A#.VkzuRg'Q5{KP3um2
"tɏ{^՝nÏ
?ൖfտ>lϏ
ك>λ#Ew'w5,6F7N|5	8DAK^b:v딋_iGNΚ 4P6&H#F;\b  \CPOi1ۆ]*itR0J4Շt^!˯-* ͜NZ>yaw^Hj-߾靣Y6w l <[ .*ykm,Ďn
A}H\ek(eJ7c,[-*<)vE@*B4nU,FE8#Ja|E,B1XS5E>uh;*ºNq}jH*HaJ
ȸFP^jӳ=G7օ6,P4=\м.NTjC(gedD<joe:p.z}f@"Ka	{vݳL"}<ys4V\xf4ք4*pA5ܴMXߊ>Q5ee3@I_S)15x+ E+}%]wcucam#2-sPuV\(QM;t~/1P*E 	]-׺e&kp;VC"#qmn4e
-u\IIz~z9C
ձC
n;{a׿_8f+VjŁNkRܽQV?;a?M>8fVa|Ld\WH:b@RT`C|~ }y	paXt8%|ZDf^7eD7~)L2XQߐro1\w~k3&q.{K1>V
ɔ5FPɇ\U"B\7]a(U9>֥Ƞ!
 ݆R}a[=Cz8A
0LWe sXy>招Mk%@ACV去70Jy^',?s}ߒ]UVNEwgtdZs|HH~sn7pJ7u5#rx&Yi[Q3Ӛ6sd@f1R;N)_|	J4@4>2ZQbK<$r)]W|V{u8ك&}BFhL`5\шzA!J
^^^IUp00,Pt<tjf\,F%헪6r7SQO&6@|1%N 4ݱb;muh\GSU['ߍލwsvm4ew_{/BI#'.u8k
Р!1RF/rĀ&qH\_^37m3CV씺P8ojXP%x K\cZt83pF~11ڢ^pW &"⛠q^iW9
8qv[^SF]}=#Ai\w
+N.-@^z8G
O<TSc@o~e:+Մl9QԊ> /YE)q$+]&_o zLdUGeMו-*o-'"4>6d&=)6b9Icc_D?V.6u^:r̡bJ53`#й'+v~87)7n:K64ĎUYdiz`]a_)Uj"9#Cst=uR]65.]<GĦ~@С~{ojqwic
WqQ	~e
Imj i8U#-Sƭ%dd]аi;+8RGfWGފ"晚DE5+w2}Be?B7


[[FILE_START: README.md]]
File: README.md
Language: Unknown
Size: 4,410 bytes | Tokens: 50
----------------------------------------
[Error reading file: GitInsight.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/hooks/fsmonitor-watchman.sample]]
File: .git/hooks/fsmonitor-watchman.sample
Language: Unknown
Size: 4,726 bytes | Tokens: 1,386
----------------------------------------
#!/usr/bin/perl

use strict;
use warnings;
use IPC::Open2;

# An example hook script to integrate Watchman
# (https://facebook.github.io/watchman/) with git to speed up detecting
# new and modified files.
#
# The hook is passed a version (currently 2) and last update token
# formatted as a string and outputs to stdout a new update token and
# all files that have been modified since the update token. Paths must
# be relative to the root of the working tree and separated by a single NUL.
#
# To enable this hook, rename this file to "query-watchman" and set
# 'git config core.fsmonitor .git/hooks/query-watchman'
#
my ($version, $last_update_token) = @ARGV;

# Uncomment for debugging
# print STDERR "$0 $version $last_update_token\n";

# Check the hook interface version
if ($version ne 2) {
	die "Unsupported query-fsmonitor hook version '$version'.\n" .
	    "Falling back to scanning...\n";
}

my $git_work_tree = get_working_dir();

my $retry = 1;

my $json_pkg;
eval {
	require JSON::XS;
	$json_pkg = "JSON::XS";
	1;
} or do {
	require JSON::PP;
	$json_pkg = "JSON::PP";
};

launch_watchman();

sub launch_watchman {
	my $o = watchman_query();
	if (is_work_tree_watched($o)) {
		output_result($o->{clock}, @{$o->{files}});
	}
}

sub output_result {
	my ($clockid, @files) = @_;

	# Uncomment for debugging watchman output
	# open (my $fh, ">", ".git/watchman-output.out");
	# binmode $fh, ":utf8";
	# print $fh "$clockid\n@files\n";
	# close $fh;

	binmode STDOUT, ":utf8";
	print $clockid;
	print "\0";
	local $, = "\0";
	print @files;
}

sub watchman_clock {
	my $response = qx/watchman clock "$git_work_tree"/;
	die "Failed to get clock id on '$git_work_tree'.\n" .
		"Falling back to scanning...\n" if $? != 0;

	return $json_pkg->new->utf8->decode($response);
}

sub watchman_query {
	my $pid = open2(\*CHLD_OUT, \*CHLD_IN, 'watchman -j --no-pretty')
	or die "open2() failed: $!\n" .
	"Falling back to scanning...\n";

	# In the query expression below we're asking for names of files that
	# changed since $last_update_token but not from the .git folder.
	#
	# To accomplish this, we're using the "since" generator to use the
	# recency index to select candidate nodes and "fields" to limit the
	# output to file names only. Then we're using the "expression" term to
	# further constrain the results.
	my $last_update_line = "";
	if (substr($last_update_token, 0, 1) eq "c") {
		$last_update_token = "\"$last_update_token\"";
		$last_update_line = qq[\n"since": $last_update_token,];
	}
	my $query = <<"	END";
		["query", "$git_work_tree", {$last_update_line
			"fields": ["name"],
			"expression": ["not", ["dirname", ".git"]]
		}]
	END

	# Uncomment for debugging the watchman query
	# open (my $fh, ">", ".git/watchman-query.json");
	# print $fh $query;
	# close $fh;

	print CHLD_IN $query;
	close CHLD_IN;
	my $response = do {local $/; <CHLD_OUT>};

	# Uncomment for debugging the watch response
	# open ($fh, ">", ".git/watchman-response.json");
	# print $fh $response;
	# close $fh;

	die "Watchman: command returned no output.\n" .
	"Falling back to scanning...\n" if $response eq "";
	die "Watchman: command returned invalid output: $response\n" .
	"Falling back to scanning...\n" unless $response =~ /^\{/;

	return $json_pkg->new->utf8->decode($response);
}

sub is_work_tree_watched {
	my ($output) = @_;
	my $error = $output->{error};
	if ($retry > 0 and $error and $error =~ m/unable to resolve root .* directory (.*) is not watched/) {
		$retry--;
		my $response = qx/watchman watch "$git_work_tree"/;
		die "Failed to make watchman watch '$git_work_tree'.\n" .
		    "Falling back to scanning...\n" if $? != 0;
		$output = $json_pkg->new->utf8->decode($response);
		$error = $output->{error};
		die "Watchman: $error.\n" .
		"Falling back to scanning...\n" if $error;

		# Uncomment for debugging watchman output
		# open (my $fh, ">", ".git/watchman-output.out");
		# close $fh;

		# Watchman will always return all files on the first query so
		# return the fast "everything is dirty" flag to git and do the
		# Watchman query just to get it over with now so we won't pay
		# the cost in git to look up each individual file.
		my $o = watchman_clock();
		$error = $output->{error};

		die "Watchman: $error.\n" .
		"Falling back to scanning...\n" if $error;

		output_result($o->{clock}, ("/"));
		$last_update_token = $o->{clock};

		eval { launch_watchman() };
		return 0;
	}

	die "Watchman: $error.\n" .
	"Falling back to scanning...\n" if $error;

	return 1;
}

sub get_working_dir {
	my $working_dir;
	if ($^O =~ 'msys' || $^O =~ 'cygwin') {
		$working_dir = Win32::GetCwd();
		$working_dir =~ tr/\\/\//;
	} else {
		require Cwd;
		$working_dir = Cwd::cwd();
	}

	return $working_dir;
}



[[FILE_START: repo2file/README.md]]
File: repo2file/README.md
Language: Unknown
Size: 4,765 bytes | Tokens: 50
----------------------------------------
[Error reading file: GitInsight.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/objects/6b/5e716eaed53fa6ce253b708aae69aae04d9399]]
File: .git/objects/6b/5e716eaed53fa6ce253b708aae69aae04d9399
Language: Unknown
Size: 5,013 bytes | Tokens: 2,464
----------------------------------------
x[rH޳: (ήga-\H"ldV{><|_/@Hvqy	TeVfVUVjut}]-,-nٔwGJwuT\&2]ߩuY)YSVjYugB ̳#Pg~}ʭ%&̾ģhwYqcq$?QﳺlU܌4Ay-dR|wUySum/%EZ.8Q~IyṘ`/`mwx:QnU[+*}Z7ѱzWj[yZaF(bqUEM|N5
11Y-۝ndJjwIUR 6hq)?<K*-`~7UһY
PP4R//Q;ڎ7W/(VUe1I8o߽3DEٍr䛲n0d^DX_fF7UaMxV5~^q]G [k[<)|`۶&-`a.H$6b=MIuEQ15hiqZO}
]1xrMl؍NOi{M-xYtEC?d?D	CdJ I$U-a8#MKͮ9/4O@sOjU#!6H#[WP mR3-k2{92i[U~Y{f<mk\2v̤.a7iU}\SrT^oV?ӂjՔ*+4=6K,<iwGW"Srk6@(MC]m;lB Jq&8[QڙASOb0
.XhqI`8*L7KMJMN:E*(OLeR|Μfx{Q} Oc5]'>NL$Buui2AMXS !^5sFtS~~ϱzqIj($iDLۮx@~I{)NЇL\U3YBܮ:NKCYwT~4'03iY̛4xӼv^Vٮox~pw.Ig&qt0Mdz'19r/cx~쩝qWkQ
Mo1BB3ܸ'
aΆ^JpaS,}N2
 &m9<~JeBL&	LWʺ
UEs6.&+ 4<0>V;*s~#n8 @m"(.M,xC>S`*z2{h@tû Gsok\׮̵Vv`Vs{=H&'?Eڧ!:#yJ~ptY"0+ĩI8O}6q>}&
P<ܻ<+
#M˨JG_D~7ppn=3=x@nw81wS	@eg$k9bd-zd Difo3FLKQa{DTi͏_"i[TKï	!9h68k1]'2ۻA'I}ñ哬^ڋQ|5zsxz>Wy_FpbU!#}{,AK2uJ¨Ôo_VOdf>#ǽf<Y"H3Cڞ6w9t`fbixU%(N]nTr}t
3](,
sXH]e|4׃{2XN
ylV"]c
b>f;4
5TJNxf<epILH8!GV$1ajfeVju!nʸNRM>6
>c}/rM < =lԈE6=L$k=^Ezʐ4^փ*l
b]18פvtp F|>DEt-M@ermuyw7Yzu'<^3}	diKƃ)2%R'
o#9V]֮q"Xa1"91qzcU8.ki|'jqߤ6k(?@+kkPgHvVѵC3- -\w8$svڋrX	HHITij=Tr!`U_
f+O@3{0 	.~"GT~OpouN% O+Wb1Rz&7@I`9^7Ax[;)ql&?x;O=<N$
S#9F
b-E ZJ6ZL[BFTh(9aPrʳhRq!Ϻ[m/"R=miULVu}|w-o $O4)yC$*]UFJXeΖvCVcBoo5Z8$e	}>@r3Üm`ʹRuچcS:ky<,3JHC=Ce4>)L7,SY֣(}2<޲]XG\l
ztР?[LΆC(D+2r[Vf^n^`YW!~q<*+zw*yM`@eڷHFxbQ?P~-I#dQZf_RCc8$KFfJE
m.wQVA&@m"|nTQ^n.I?ĈN=v;ǖdٚ6&A۩wa\G`9xS![3yVy##ޅw:UzKf`T\PaBo5:[=85^1˪=:v?iJ?G=RS' [P+x_aɓֹ{eEbZ
rQˌ:j(t
=y*ns]KBZLb׉^G0iYE,j*C3FkGgzx'#Nb9r3LYh߬OHI:ӵW?<
w^՟Pr#')V)\ҸrdG~ξr]ԎFƯPVpwϋ>ֽĪJ	]6Jr-qBZݱn!~Sh)ooJJh5*|rT-QݑF旇':t%dݚz?J6FX,?bn-J۲(?'(g1@G㰷}_b׉]DxhG:LOg
OiQGIB"zTEO{`HF>wbju׫?
prnX
^zG`ĆP_6ЗeaHLtyuG
rZPF|Qp!ߠߌ:nڠD?MV0bgҧ>'U9[7'
5UXa'&/[)GPh赔L	PA۾ ҆A-z񕂝$sznYiL~1shpAw̢B-b{hRqa&REPw$z]O8m/QBlv&链v=VNi䌱Uҽ
ސvu:	kh%!aOE yvcV%ƈU@[K6NEWi6-%칀֖ҹXOu-jS2"yk
ۼ@,<rm(eioC8us/#D-\-Ӟ-midI9(򴍘޾p<o;4!/hY),XlT&)g;
Ӵ}`SEU^M$8뢎L&f6OPb˩ON1T>=Io;i]<~x= Y"(0\m*.ST$#:v5MeJ%7}1NI.e낆5pG,@;8ר/
pl4_O>aae]!F>v/pG+R{Ƣ6aXb
g>HVex0v	VP8p*O»;p~8(lov'CL\={KpuFh}ͽYL\~$\hbUY%<j-epu8{)'l`\:E^ΓUMCO3R
,:h([+dMZ".b̙U2ٷ Բh.5W1ō\s撝>:&-AO\z$zP!iX0kv',^Hk=`_?bZЇ@x~-u3eOqh,7KD4j˶|n{%:>OU'fB-f\C Kٞ/}enxo1*1BLt<"[9dC
Q]&<;?i`z|&]~F\.@`[nmKWȢ^SSFt@׶Jct(A	JPs)XReО32a#W9nn%0#"s,Ól@̕S .ņ0pq2pI[h{A	 `>՘$yEd&{;


[[FILE_START: test_ui_branch.html]]
File: test_ui_branch.html
Language: Unknown
Size: 5,038 bytes | Tokens: 1,127
----------------------------------------
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Branch Selection UI Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .test-container {
            border: 2px solid #ccc;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }
        .github-input, .branch-input {
            margin: 10px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .status {
            padding: 10px;
            margin-top: 10px;
            border-radius: 4px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>Branch Selection UI Test</h1>
    
    <div class="test-container">
        <h2>GitHub Repository with Branch Selection</h2>
        
        <div class="github-input">
            <label for="githubUrl">GitHub Repository URL:</label>
            <input type="text" id="githubUrl" placeholder="https://github.com/username/repo" value="https://github.com/octocat/Hello-World">
        </div>
        
        <div class="branch-input">
            <label for="branch">Branch (optional):</label>
            <input type="text" id="branch" placeholder="main" title="Leave empty to use the default branch">
        </div>
        
        <button onclick="testBranchSelection()">Test Branch Selection</button>
        
        <div id="status" style="display: none;"></div>
    </div>
    
    <div class="test-container">
        <h2>Test Cases</h2>
        <button onclick="runAllTests()">Run All Tests</button>
        <div id="testResults"></div>
    </div>
    
    <script>
        function testBranchSelection() {
            const url = document.getElementById('githubUrl').value;
            const branch = document.getElementById('branch').value;
            const statusDiv = document.getElementById('status');
            
            statusDiv.className = 'status success';
            statusDiv.style.display = 'block';
            statusDiv.innerHTML = `
                <strong>Test Configuration:</strong><br>
                URL: ${url}<br>
                Branch: ${branch || '(default)'}<br>
                <br>
                <strong>Expected Behavior:</strong><br>
                ${branch ? 
                    `Clone specific branch: <code>git clone -b ${branch} ${url}</code>` : 
                    `Clone default branch: <code>git clone ${url}</code>`
                }
            `;
        }
        
        function runAllTests() {
            const testCases = [
                { url: 'https://github.com/octocat/Hello-World', branch: '', expected: 'Default branch' },
                { url: 'https://github.com/octocat/Hello-World', branch: 'test', expected: 'Specific branch: test' },
                { url: 'https://github.com/octocat/Hello-World', branch: 'develop', expected: 'Specific branch: develop' },
                { url: 'invalid-url', branch: '', expected: 'Should fail validation' }
            ];
            
            const resultsDiv = document.getElementById('testResults');
            resultsDiv.innerHTML = '<h3>Test Results:</h3>';
            
            testCases.forEach((testCase, index) => {
                const result = document.createElement('div');
                result.style.margin = '10px 0';
                
                const isValid = testCase.url.includes('github.com');
                const status = isValid ? 'success' : 'error';
                
                result.innerHTML = `
                    <div class="status ${status}">
                        <strong>Test ${index + 1}:</strong><br>
                        URL: ${testCase.url}<br>
                        Branch: ${testCase.branch || '(default)'}<br>
                        Expected: ${testCase.expected}<br>
                        Result: ${isValid ? '✓ Valid' : '✗ Invalid URL'}
                    </div>
                `;
                
                resultsDiv.appendChild(result);
            });
        }
    </script>
</body>
</html>


[[FILE_START: .git/objects/13/24bc6b605e48466c5744097be1fe5345651061]]
File: .git/objects/13/24bc6b605e48466c5744097be1fe5345651061
Language: Unknown
Size: 5,186 bytes | Tokens: 2,574
----------------------------------------
x[rHvε HX$מuFX   %+ZU;6Wy}|_2	tӧO>\R]|p}]-,-nٔwGJwuTJnb&͇j]Vu֔սZE]Y7YYdݕUVy|d~-ݷ_k@rvqɳ2/]Vv\$Oԇn,&ۦzv6cMPja}&^bWfk>лҺD]"ޔ~[Kclap<.aC0XMŎ^S0¶c	<(nU[ˊ*>XP+-}G81Y=wHyL&p@,#ҬvgYZݢn"`Qoc96GzasZ,⻸r؂{ySŽkё)N#2{J:WZf?}PSvB,7i3~z{Ż.01:QѦiv\x^DXDg7UaMxV5~Q4k*p49Rn[g+ǚOD vS4~ÈAQө&;L@CuO!+f'7}'Fߴ=ͦVpY"wEE_<DɆ):Mjݧő5mZrvnvx1!5(x"ߍ_6jY}~w<OY^`
T~54,	k
ӳvC:?\SSރP?i[~Y [l3婜]UdZ+IoҪvEJN)`vӂjՔ*+4=6K,<iwGW2iܭ9>!k
iCw)pMtL(4)[J?^&nRY6@]+1QX#L6)>G˸_Y{zO6Z
PE^`V*iyRsG)MaDiC ZbOh	Br'زK}*(|_b$c͞
ƻ
5\f2O2ߧsg\gg%$ 8(`8;3_2w:V&,(K
d,_ ~"HV͂?NXgؤ
rQҒFKԚրm3Ft t9Iv'\}n'0ri8Q\_D+P	~^di?E`,!g{ck 
4	WUkxxp喽t#:dLӱZw ,r7ex$aC$:v~A.!fhT4v`H{+PL56"g]ؘ2نAHgE6mʞ<y?l#&f1]܆llR1F*3)(}20
&xjVi
!A!JJ1y3Wʴ#/>f,p$r`Ѐ
wyZA;5׈ɍ]skC8N
أ
,z<`%&Χ?E'!:}K#cyJ~p|Y"Bxi8O}+ur>}Pyv9<ִ4N8b
'JyH 3NN4;&!OA)@O?
wqD;rDX7wSuHgϪ4>^
#lmOUrX4w-HzK/	_iC0zA `(`֘/֏'I&4:j.Z/מb<P7s)žbyi+JL[JOy
ujhԉDV͗8~9DJ`N_BK=Ț?AtjU\]iOG!ٙ/lY%ˍ]sEfe(HC׵iQƴx=xpy6$՛8YGqv}rsģ+uAɻUW+ǘ$+zig0XxV4xF(҂$oD
F2GSjDm2H9
(:5Yd-|k==Y|y8b9Jͩ1`N33Nh@	.eEXΑ"%kHN{6VbІI&#s4ÇB**nA\
D08wy޾*6Y5'L\'	w+>$VXO1	lro/[w-]F&D^٦fD~|?F] tSҢ!;yT&Fx#	N^8Uzv;Ehz2Hs([sv`ڋs	HWn
Zۤ~S*E5P5`~ O40	9":Ө
"Vdj A590 n, \J6iU0	ˤL/^z;=<ҩ|#Ȇf"tr-qF-&X#1*BjEt)	A<jcn\oݭaV@T^	ݺzp]M:"2'ѼC+ת\#$w*[g+zK.5V7зB-Hbmyg`b+`1f/!wAx-;GR̞`f#4#^E#J=d6Ogi7җh@[k>V vtBotdŉ8zb_ˬG;
ÅTrZ	SfHD񊹌ڋCWj+EoJ,껯 ?k?ep[;ȼ12pmFcXa
ӈ?Q~)bGӣZd_RBF2[KDfHE
u&wYV@m"|nTQG_ܴ.EG;wcy2MlA;7.F#0)[ґ"+ּoLO{&:WgbK>*=%#0[S(0`\^1U,2oh)z0@urO
3kX%7 ۀR^{Xy~o)jk<#>ȨģmN5L7&AcW7.k_iE}t")\~RX u>wn@yS \(̀ɔa>|ÌF* 17M)Xc+"xJmTqqG940F4.q_/\£+k"L~PvoeU%ُwCq×8!-j?!pݷ7%_gv%4T{6a8pQ$D_wGvYzo^ޱuk\_q4Wrփ&"s{ZPMEa[8E!
hkYl3qZED=>e4)hƕGu.&	%l}EKDb-aPT#c91\է Hƃd]վ`HOջ6#օa=Sl^FUڤ4@x=L;ޔlgJ6̎[fTqs%
'i`#v+}UAPUypRS-o'1}aڙk)+cs?,\
/H!Ak+;HDݲG3ŘuЯ
%EuełPC[WMv [	ܥ=]c촽Po
}ؙOڨX6$c髤Y!%eΙk0s֐<(K\C$6}5@3wc*R TK6/M8\9Xygõ~c4:j[[eI-U3ZkDD*y/7AY8x\A-&I3T"rq
5^F2m[p=gsPivżN\jEQnKB킶}E큶{dYΪB5m[[`TQD?h1u]ԑ)լa#f^N9r9II1Mxh

!u!6b&@ dVۈ_
*EL"r]fnc;ZӋFKH3Gշ@mܥ]߸N14vCy)ao|x^|ӆx
c
3\5_>XMksky܇cw"?Ǚ$U8&e{Ӥ`'t;-{g_7݉lgo	ъ◺Oó0>W_1H?'XU
@V!|FЁ_gc0%2w68O20H.*
.ԍiQ$^1.%o_z~4#)P@26@B_Z kRit1v9s5JsI1!
K͋2[y:DZ5gk.b֩skJrRd
xx:B0ҰD=@ad9OZXPӽhziiA{n)mCS`]""Q[;eox*K?ul%3fB-͸xQ.A6v=_	 >ޢćUcy`RJ
q4ZL |	&xwT~R+DkMBŹ%<MY âw<1&ȢVSSF4栉k	:Рm`/[(͹~Q2Nhϙm		He|L*a7%lFY$ ^\l@̕ ~&źw l0rYe!A[}i[A	 -`_,P̊"ҬD030


[[FILE_START: UI_IMPROVEMENTS_SUMMARY.md]]
File: UI_IMPROVEMENTS_SUMMARY.md
Language: Unknown
Size: 5,577 bytes | Tokens: 1,205
----------------------------------------
# Repo2File UI Improvements Summary

## Overview
This document summarizes the comprehensive UI/UX overhaul implemented for the Repo2File web interface, transforming it from a basic light theme to a modern, production-ready dark theme with purple accents.

## Features Implemented

### 1. Dark Theme with Purple Accents (Feature 1)
- **Color Palette**: Implemented a sophisticated dark grey palette with vibrant purple accent colors
  - Primary background: #1E1E1E (very dark grey)
  - Secondary background: #2D2D30 (container backgrounds)
  - Text colors: #E0E0E0 (primary), #B0B0B0 (secondary)
  - Accent purple: #9A5CFF with darker (#7B3FE5) and lighter (#B685FF) variants
- **Consistent Application**: Applied the new theme across all UI components
- **Enhanced Readability**: Ensured excellent contrast ratios for text visibility
- **Code Block Styling**: Special dark background (#1A1A1A) for code output

### 2. Enhanced UI Elements (Feature 2)
- **Typography**: 
  - Upgraded to modern font stack: Inter for UI, JetBrains Mono for code
  - Consistent font weights and sizes throughout
- **Button Hierarchy**:
  - Primary actions: Purple accent color
  - Secondary actions: Dark grey backgrounds
  - Success state: Green (#4ADE80)
  - Error state: Red (#FF5A5A)
- **Interactive Elements**:
  - Smooth transitions (0.3s ease) for all interactive elements
  - Hover states with subtle background changes
  - Active states with transform effects
  - Focus states with purple outline for accessibility
- **Input Fields**:
  - Dark backgrounds with light text
  - Purple border on focus with glow effect
  - Consistent padding and border radius
- **Drop Zone**:
  - Enhanced active state with purple border and glow
  - Smooth transition animations
- **Loading Spinner**:
  - Purple accent color for the spinning element
  - Dark grey base color

### 3. Image Asset Validation (Feature 3)
- **Analysis Result**: No image assets found in the UI
- **Recommendation**: Consider adding an SVG logo for branding
- **Future Consideration**: Any images added should be optimized and have proper alt text

### 4. Production Readiness (Feature 4)
- **HTML Semantics**:
  - Added semantic HTML5 elements (header, main, nav, section)
  - Proper heading hierarchy
  - Meta tags for SEO and description
- **ARIA Support**:
  - Full ARIA roles for tabs (tablist, tab, tabpanel)
  - Live regions for dynamic content updates
  - Screen reader announcements for user actions
  - Proper labels and descriptions for form elements
- **Accessibility Features**:
  - Screen reader only content class (.sr-only)
  - High contrast focus indicators
  - Keyboard navigation support
  - ARIA live regions for status updates
- **User Feedback**:
  - Enhanced copy button with success animation
  - Error state animations (shake effect)
  - Screen reader announcements for actions
  - Visual and auditory feedback for all interactions
- **Responsive Design**:
  - Mobile-optimized breakpoints
  - Flexible layout adjustments
  - Touch-friendly tap targets
- **Performance**:
  - Google Fonts preconnect for faster loading
  - Optimized CSS transitions
  - Minimal animation usage for performance

## Technical Improvements

### CSS Architecture
- CSS custom properties (variables) for maintainable theming
- Organized sections with clear comments
- Modular approach to component styling
- Consistent naming conventions

### JavaScript Enhancements
- ARIA attribute management for tab switching
- Enhanced error handling with visual feedback
- Screen reader announcements for dynamic actions
- Focus management for better keyboard navigation

### Cross-browser Compatibility
- Vendor prefixes where necessary
- Fallback values for newer CSS features
- Standard-compliant code

## Visual Impact

The UI transformation includes:
1. **Modern Dark Theme**: Professional appearance preferred by developers
2. **Purple Accent Color**: Distinctive branding that stands out
3. **Smooth Animations**: Subtle transitions that enhance user experience
4. **Clear Visual Hierarchy**: Easy to understand interface flow
5. **Professional Typography**: Clean, readable fonts optimized for screens

## Accessibility Compliance

The updated UI follows WCAG guidelines:
- **Color Contrast**: Meets AA standards for text readability
- **Keyboard Navigation**: Full support for keyboard-only users
- **Screen Reader Support**: Comprehensive ARIA labels and live regions
- **Focus Indicators**: Clear visual indicators for focused elements

## Production Readiness Notes

For deployment, consider:
1. **Minification**: CSS and JS files should be minified
2. **Asset Optimization**: Any future images should be compressed
3. **Caching**: Implement proper cache headers for static assets
4. **HTTPS**: Ensure secure delivery of all assets
5. **Performance Monitoring**: Track UI performance metrics

## Future Enhancements

Potential improvements to consider:
1. **Theme Toggle**: Add light/dark theme switcher
2. **Custom Themes**: Allow users to customize accent colors
3. **Animations Settings**: Provide option to reduce motion
4. **Icon Library**: Add consistent icon set (possibly using SVGs)
5. **Loading States**: More sophisticated loading animations
6. **Progress Indicators**: Show progress for long operations

## Conclusion

The Repo2File UI has been successfully transformed into a modern, accessible, and visually appealing interface that matches professional developer tools. The dark theme with purple accents creates a distinctive brand identity while maintaining excellent usability and accessibility standards.


[[FILE_START: CLAUDE.md]]
File: CLAUDE.md
Language: Unknown
Size: 6,623 bytes | Tokens: 50
----------------------------------------
[Error reading file: GitInsight.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/objects/32/68b4c851ff31fc4b0b5634ecd8151286ba9d30]]
File: .git/objects/32/68b4c851ff31fc4b0b5634ecd8151286ba9d30
Language: Unknown
Size: 6,720 bytes | Tokens: 3,244
----------------------------------------
x\mSI
q3 =;K'rP4RږArqqa>ޯ_rϓ<s{
Vweeefe[Ub_O~MyQ\3e6.򩪖lvì6I?Uϒɦz
+o<&6ͦ)pںzHB
YY%\{Ύ~:~~!0G'
wv^uwG'x~_v72e6H_ӛTG\\.'م|{6kr\\/rMdy/ϗC'IYʷl*Mu>_
HWݻoN_
gk
c>{r{ͲqO_h~*XyF p-g]b*4$~A!q6IK՛'eEMVÍe:Kc0o3!NU 
m94.@\9^MShɰBM襠n]eRi֛3a~iNtw(z,
+u(+D+@9fUv9",-#ݳZL/H쫓	HQZ~y@/NwiW7!^;/>`xj M><ӵ;2UR*_LF**
UVbX-T4)M5+5^L&U:N>}wPK92$SiU,lI4akWzN pn:Bi/Ted1J32];xiWoMQ͝zVy$_pm\Q8)YN!NaLfPx)F`D#B[΋S:@u_fNtWxZPplݖ_rJg_M2
\c5O27Z	? IuK%P[?͜*-f%:d&vU2cSF~UW*3
JJJ5pºכ,Mܐ6>IQ]^Zhc7c&07U4+@0FN|׉Ud|2Y5@䶥L	K2bd"-h1\M'Jr?|Q`?iH}$WQJ$ 3znG>[ykRLQ
Ho5V2[Pb?3W>+jbB瓬A!u2)SɈby]:t^^pD,JMF|҈vG_QDAN[c
0GhA\EoY"vq}}r"gwj 2\ܿ\e)-G̍{R.̈Lfwxi>\=`p/dcS{ӥhxÅe\b/|Q6L}DD'](Vh
+ȼ|5/%D8(H`Rɲw6dg'6NCY.ӝMsgYn|K'^gzB`
.@TmA$RP?3?ybD0^ʌ.C|4m]ݓy2v%9c(cq`Mkq-C*
ZE_0!~]TZ׉:`@:˅=mTKoG*O	I jȈ6_s@hfNMgxb	$E8,LR&E1iH&}KN}N}ɒIEf4}ޙg$3@!P"P"wN{6>3اt`i\&E:Q&@W^|*.L0sY3;@4dl۱S\OVvD?m!+Y+R-Y-8TǇTy᲋|֟JS'j h
y3dn^zu̍pIbW0ȃ갬S&YRRH1w:d$85 2=./1)ȃ\tR
ݩeռ:-#o`	8#4k1E\n*)l2F64f:)v	|U4h﫳G/Y<ʯYԖ&ҖsNgOI+<cfLQGvzÀm}l
~.g^Y%EL5MkTRX ͶCne?j5OrSH{&HQ)խ_IwZ6Y	9]s.
.J PhV6L&Յx4B:(i]֔(B0vV1h\~jL<aXt
XV~b y!d/QaM(:ā?Pk\RU+B1Djڀ[=bAy(X'MqxK$/
STcCYs1Yx">l.uguß[E7(ʊQe;BQAƝ[nN'y]Gf鋎JXZkz8]Sr^2zDBJA
	Hsvϊ{XFen&ߝwolH2QB"!+-'i8uEq?'v)j4RrIaA0slY&qw;_vv%)hzngxg0Gvۮ1@,
:	R쁈rc`[o)hv_㭵rLh9ޅb E,M*(
!b_hDe(LAmL":-M.Z ql	f]P4mWm;$6f#V
+Zll{ta^gi:lu*6'NEWGc8} iжSU(-8蜃BQfK?)p&[834arqv#UsTHU̂N+'hJD
`S}N'b(ףJ5+ImT7cuS%E䆆ƴK4`b*Ӗ "i&GG=~J<G` ;@Nf:
ɲik&Y/?Ս,h% )SSvHG/
RMED (OZSBuwAN*5qm!k(0Qu]FATH͌J=#>!Ze+(ii^gQ[?FG=,*C<cryxHJnքcdoMo`ƷukX_
#B'8AX)bMW{=6C.@_2L/nX_gĄ	'jtMP]&رXҜ|dqt:/>h;;Yٷjê9qUL[E"ڻLBkŀu	ȕTQq0NQEpokq(PuDqA*}^ {D=
3<;,:Ox"h<^. 'bpeCR76!a<opP-Dr-
E</'}/BO!RO)&U
(=;=}|Y}C	X`c#>.XUm@Ff2160{|FaK>`إaygxЬS=kBxZ\l?˪?,.PuIr5%UɅzywy02kcᓯrFKXtw㑄cYXwE!gY
FFL ;iZn)|gKy4^e砜kٺcg}s)XNL]cAGYLtrhB*ѱKOu{T:ISJ	l2cM㫚Fx~K:o)<#"[!?eެLf]Vc;?4Xv	h|~sH @kLDO$ˎ6u']!ӮF<2z~VӲ#SJ&v-u;~O?oKoG'>	&Ԧ-
v:4;kGf(#%Q+vzD0VXRtUca
po#|uQH(hr3Bz 	ۣcl`?O!7GP HP7aU# PqN[7Ԣzlf44cQ=k4cE	QO䋏tgi9P
F1AV;gV.UЇKn
]irS9X*N<IMڍhצ9O	PU&WpHiɂ?r|ПwEG
euvbmM	3`]&R@u!$ԟSDsn	Vt_}Ct	+G^ٿA	/Ϲf&= ȋWO6
jNavQ^ʺ4~*pb&ٜ&	w\'8v^%t
2SX&0{
d>c%uoŝr|..VYXOhϮzp`=-F%NlT-^ޚ;8C(W.AD L	>o^?r"s~,BgsVkVKF-
ؘ;d˺s ź1h7:bM^|5s
GHuYQVT޶|@~t
n1F1z@}Y\;{!(?8¦Ȇan<9-71ga68}BSĎ]mĴ4p\)k&C7&-B!>>;߸>|>e"fG<GM_{+&ćX>
FtusTx=
A[z&ZĒy̙Myϟ2U8s9GIX@;[[ C^T$T>Нǐ^ڬ
Nӄx˚:3	gokojD5iv
h^>v-VDx̆)z
#4tՀ/kxNPTįrɷT70XMvPᶄ4"	|-GZ'9>p7N!@`2Ľ<5V|%Y~G_,XSĬ#KRgWc?ұ}%
Q"dWBR8u$yPㅓM6QySxPE-E^ڏ[wȄPXconǴ{u WQډ{+Q,8wA9g9ւKF1J[Dm[h˜"4`,6Q,kehWT>r՜XvX	TNXCb
n)dاuE[k B8* 
HS~H4+%1vXxwT/[ʞi!ر=7.nכ9l?<fW
M΁(YJf# pR|x[ߩԬpj `2NX'?6@0o^=WʣǝFBC91?5dFΫEd55q<W6aRMB
Ki+s/
xCΧ#.hHJ@`/ݸKTkrwC:vL6RzjՖ-(:4;ߴ:wY+E6ޭ;&*
~Lw-&ZD{dE3w[{?j/h(CPkv
eVR 
 BES y!ol"sy/~NxjtHGitZ(պy?A YІ\nR~o/wy'#Tp%s3Y\j0#7~aKZgCĻ%'8LBZ<{ـny6`J(B;iT`#i0Z	ΣWI 3dޓe=awxaf0Dl\ؓYoyH %#M4+K:,7{\wPO<Kc֍ZrҮc0%,Xgt/&ٮ<DPY?HSٺ%lMAm9+|r?W}u	"@E6Xgg
?FsAGHl2tnY`


[[FILE_START: AI_ACTION_BLOCKS.md]]
File: AI_ACTION_BLOCKS.md
Language: Unknown
Size: 6,721 bytes | Tokens: 50
----------------------------------------
[Error reading file: TodoItem.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: docs/GEMINI_FEATURES.md]]
File: docs/GEMINI_FEATURES.md
Language: Unknown
Size: 7,520 bytes | Tokens: 1,702
----------------------------------------
# Gemini 1.5 Pro Support Documentation

## Overview

BetterRepo2File now includes comprehensive support for Gemini 1.5 Pro, Google's large context window model. The Gemini profile is specifically optimized to take advantage of Gemini 1.5 Pro's 1 million token context window, providing enhanced features for processing large codebases.

## Features

### 1. Large Token Budget (1M Tokens)

The Gemini profile is configured with a 1 million token budget by default, allowing you to process significantly larger repositories without truncation.

### 2. Hierarchical Manifest Generation

When using the Gemini profile, a detailed hierarchical manifest is automatically generated, including:

- Project overview with type, language, and frameworks detected
- Navigation guide for easy browsing
- Directory-based organization with estimated token locations
- File importance scoring
- Module/directory purpose detection

### 3. Advanced Truncation Strategies

The profile uses the `middle_summarize` truncation strategy, which:

- Preserves the beginning and end of files (most important parts)
- Intelligently summarizes middle sections when needed
- Prioritizes business logic and critical code sections

### 4. Business Logic Prioritization

The semantic analyzer identifies and prioritizes:

- Revenue-related code
- Financial calculations
- Core business logic
- Critical algorithms
- Main entry points

### 5. Automatic Configuration

When selecting the Gemini profile:

- Ultra mode is automatically enabled
- Token budget is set to 1,000,000
- Model is set to `gemini-1.5-pro`
- Manifest generation is enabled
- Advanced truncation is configured

## Usage

### Web Interface

1. Select "Gemini 1.5 Pro (Large Context)" from the profile dropdown
2. The interface will automatically configure:
   - Ultra mode: ON
   - Model: gemini-1.5-pro
   - Token budget: 1,000,000
3. Process your repository as usual

### Command Line

```bash
# Using the Gemini profile
python repo2file/dump_ultra.py /path/to/repo output.txt --profile gemini

# Equivalent manual configuration
python repo2file/dump_ultra.py /path/to/repo output.txt \
  --ultra \
  --model gemini-1.5-pro \
  --token-budget 1000000 \
  --truncation-strategy middle_summarize \
  --include-manifest

# Process a specific branch
python repo2file/dump_ultra.py /path/to/repo output.txt --profile gemini --git-insights
```

### API

```python
# Using the REST API
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "gemini",
    "github_url": "https://github.com/user/repo",
    "options": {
      "github_branch": "develop"
    }
  }'

# Or with explicit options
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ultra",
    "model": "gemini-1.5-pro",
    "token_budget": 1000000,
    "truncation_strategy": "middle_summarize",
    "include_manifest": true,
    "github_url": "https://github.com/user/repo"
  }'
```

## Example Output Structure

When using the Gemini profile, the output follows this structure:

```markdown
# Repository Analysis Report
==================================================

Repository: YourProject
Generated: 2025-05-18 08:55:55
Processing Model: gemini-1.5-pro
Token Budget: 1,000,000

## Project Overview
Type: Python Web Application
Primary Language: python
Total Files: 150
Total Size: 2.5 MB

# Project Manifest

## Table of Contents

### Project Overview
- **Type**: python Project
- **Primary Language**: python
- **Key Frameworks**: Django, React
- **Total Files**: 150

### Navigation Guide

Each section below contains:
- Module/directory purpose (when detectable)
- Key files with their main exports/classes
- Estimated token location in the output

---

### Root
*Project root directory*

- **README.md** - Project documentation [Token offset: 1,000]
- **setup.py** - Package configuration [Token offset: 2,500]
...

### src/api
*REST API endpoints*

- **src/api/views.py** - API view controllers [Token offset: 10,000]
  - Classes: UserView, ProductView, OrderView
  - Functions: authenticate, validate_request
...

[File contents follow the manifest]
```

## Configuration Details

The Gemini profile (`app/profiles.py`) includes:

```python
'gemini': ProcessingProfile(
    name='gemini',
    description='Optimized for Gemini 1.5 Pro with large context window',
    mode='ultra',
    model='gemini-1.5-pro',
    token_budget=1000000,
    truncation_strategy='middle_summarize',
    generate_manifest=True,
    semantic_analysis=True,
    prioritize_business_logic=True,
    include_dependencies=True,
    smart_chunking=True,
    preserve_structure=True
)
```

## Advanced Features

### Semantic Analysis

The Gemini profile uses advanced semantic analysis to:

- Extract classes, functions, and their relationships
- Calculate file importance scores
- Detect business logic patterns
- Identify critical code paths

### Smart Chunking

Files are chunked intelligently to:

- Preserve function and class boundaries
- Keep related code together
- Maintain context for better understanding

### Cache Optimization

The caching system is profile-aware, meaning:

- Different profiles maintain separate caches
- Cache invalidation considers profile settings
- Improved performance for repeated processing

## Best Practices

1. **Use for Large Codebases**: The Gemini profile excels with large repositories that would exceed normal token limits

2. **Review the Manifest**: The hierarchical manifest provides an excellent overview - use it to navigate the output efficiently

3. **Business Logic Focus**: If your codebase has critical business logic, the Gemini profile will prioritize it automatically

4. **Token Monitoring**: Even with 1M tokens, monitor usage for extremely large repositories

5. **API Integration**: Use the profile parameter in API calls for consistent configuration

## Troubleshooting

### Token Limit Exceeded

Even with 1M tokens, very large repositories might exceed limits. Consider:

- Using more specific file filters
- Excluding test directories
- Focusing on specific modules

### Performance Issues

For optimal performance:

- Enable caching (default)
- Use parallel processing (default in ultra mode)
- Consider excluding large generated files

### Manifest Not Generated

Ensure:

- Ultra mode is enabled (automatic with Gemini profile)
- Sufficient files are processed
- No errors during semantic analysis

## Future Enhancements

Planned improvements for Gemini support:

1. Dynamic token budget adjustment based on repository size
2. Multi-stage processing for extremely large codebases
3. Enhanced business logic detection patterns
4. Integration with Gemini's code understanding capabilities
5. Custom manifest templates

## API Reference

### Profile Endpoints

```bash
# Get Gemini profile details
curl http://localhost:5000/api/profiles/gemini

# List all profiles
curl http://localhost:5000/api/profiles
```

### Processing Options

All standard processing options are supported, with these defaults for Gemini:

- `mode`: "ultra"
- `model`: "gemini-1.5-pro"
- `token_budget`: 1000000
- `truncation_strategy`: "middle_summarize"
- `generate_manifest`: true

## Conclusion

The Gemini 1.5 Pro support in BetterRepo2File provides a powerful way to process large codebases while maintaining context and structure. The combination of large token budget, intelligent truncation, and semantic analysis makes it ideal for comprehensive code analysis tasks.


[[FILE_START: VIBE_CODER_FEATURES.md]]
File: VIBE_CODER_FEATURES.md
Language: Unknown
Size: 8,084 bytes | Tokens: 1,837
----------------------------------------
# Vibe Coder Features - BetterRepo2File

This document describes the new "Vibe Coder" features added to BetterRepo2File that enhance the workflow between Gemini 1.5 Pro Preview (for planning) and Claude Code (for implementation).

## Overview

The Vibe Coder features transform BetterRepo2File into a sophisticated bridge between AI planning and AI coding systems, making it easy for developers to:

1. **Articulate their high-level goals** ("vibes") and get them formatted for planning AI
2. **Integrate plans from Gemini** into rich context for Claude Code
3. **Navigate code with textual anchors** for precise AI instructions
4. **Prepare iteration feedback** for continuous improvement cycles

## Feature 1: Vibe & Goal Input with Gemini Planner Primer

### UI Components
- **Vibe Statement Input**: A text area where you describe your high-level goal
- **Location**: Ultra Mode settings in the web interface

### CLI Parameters
```bash
python dump_ultra.py ./myrepo output.txt --vibe "Improve checkout speed" --planner "plan.txt"
```

### Generated Output Section
The tool generates a special section at the top of the output file:

```
==================================================
SECTION 1: FOR AI PLANNING AGENT (e.g., Gemini 1.5 Pro in AI Studio)
Copy and paste this section into your Planning AI.
==================================================

MY VIBE / PRIMARY GOAL:
[Your vibe statement here]

PROJECT SNAPSHOT & HIGH-LEVEL CONTEXT:
- Primary Language: Python
- Key Frameworks/Libraries: Flask, React, PostgreSQL
- Core Modules/Areas:
  - /app: Main application logic
  - /api: REST API endpoints
  - /frontend: React UI components

AREAS OF RECENT ACTIVITY / POTENTIAL CHURN (Git Insights):
- Files with most changes (last 30d): payment.py (15 commits), cart.js (12 commits)
- Key files recently modified: api.py (john_doe, 2024-01-20)

SUMMARY OF KNOWN TODOS / ACTION ITEMS (Top 5-10):
- [TODO from checkout.js]: Optimize payment processing flow
- [FIXME from database.py]: Add connection pooling
```

## Feature 2: Claude Coder Super-Context Generation

### Planner Output Integration
After receiving a plan from Gemini, you can:
1. Paste it into the "AI Planner Output" field in the UI
2. Use the `--planner` CLI argument with a file path or direct text

### Generated Output Section
```
==================================================
SECTION 2: FOR AI CODING AGENT (e.g., Local Claude Code)
This section contains the detailed codebase context and the plan from the AI Planning Agent.
==================================================

PLAN/INSTRUCTIONS FROM AI PLANNING AGENT (Gemini 1.5 Pro):
[Your pasted Gemini plan here]

--- DETAILED CODEBASE CONTEXT ---

[Full hierarchical manifest with code, insights, and anchors]
```

### Textual Anchors System
The output includes navigation anchors for precise code references:

#### File Anchors
```
[[FILE_START: src/services/payment.py]]
File: src/services/payment.py
Language: Python
Size: 2,450 bytes | Tokens: 512
----------------------------------------
```

#### Function/Method/Class Anchors
```python
[[FUNCTION_START: process_payment]]
def process_payment(order_id):
    # Process payment for order
    order = get_order(order_id)
    return payment_gateway.charge(order.total)
[[FUNCTION_END: process_payment]]
```

### Usage Example with Claude
You can now give precise instructions like:
> "Claude, modify the function marked [[FUNCTION_START: process_payment]] in [[FILE_START: src/services/payment.py]] based on step 3 of the plan."

## Feature 3: Smart Iteration Package Builder (Coming Soon)

This feature will help you compile feedback for the next planning cycle:

### Inputs
1. Current (modified) project directory
2. Previous Repo2File output
3. Your feedback file containing:
   - Claude's logs
   - Test results
   - Your observations

### Generated Output
```
==================================================
ITERATION UPDATE & REQUEST FOR NEXT PLAN (For Gemini 1.5 Pro Planner)
==================================================

ORIGINAL VIBE / PRIMARY GOAL:
[From previous cycle]

PREVIOUS PLAN FROM GEMINI:
[Extracted from previous output]

USER SUMMARY & CLAUDE'S EXECUTION FEEDBACK:
[Your feedback content]

KEY CHANGES MADE TO CODEBASE:
- Diff Summary: 5 files changed, 120 insertions(+), 30 deletions(-)
- Key Modified Files:
  - src/payment.py: Added async processing
  - tests/test_payment.py: New tests added

CURRENT RELEVANT CODE CONTEXT:
[Focused snapshot of modified areas]

REQUEST FOR NEXT PLANNING STEPS:
Based on the above, please advise on the next steps...
```

## Feature 4: Enhanced UI/UX for Vibe Coders

### Textual Anchors
- All code entities are marked with `[[TYPE_START: name]]` and `[[TYPE_END: name]]` tags
- Types include: `FILE`, `FUNCTION`, `METHOD`, `CLASS`
- Makes it easy to reference specific code locations

### Quick Copy Snippets (Coming Soon)
- Copy buttons next to key items in the UI output
- One-click copy of anchors like `[[FILE_START: app/utils.py]]`
- Reduces manual typing when crafting prompts

### Configurable Verbosity
- Control how much detail appears in different sections
- Options for inline vs. manifest-only insights
- Customize based on your workflow needs

## Configuration Options

### ProcessingProfile Fields
```python
# Vibe Coder specific fields
vibe_statement: str = ''  # Your high-level goal
planner_output: str = ''  # AI planner's output to integrate
enable_action_blocks: bool = True  # Enable structured blocks
action_block_format: str = 'both'  # 'inline', 'manifest', or 'both'
```

### UI Settings
All vibe coder features are available in Ultra Mode:
1. Enable Ultra Mode
2. Fill in the Vibe Statement field
3. Optionally paste Planner Output
4. Configure other settings as needed
5. Generate your enhanced context

## Best Practices

1. **Clear Vibe Statements**: Be specific about your goals
   - Good: "Improve checkout performance by 50%"
   - Better: "Optimize database queries and add caching to reduce checkout page load time"

2. **Structured Plans**: When pasting Gemini's output, ensure it has clear steps
3. **Use Anchors**: Reference specific code locations in your prompts to both AIs
4. **Iterate Frequently**: Use the iteration package builder for continuous improvement

## Example Workflow

1. **Start with a Vibe**:
   ```
   "Improve the performance of our checkout process"
   ```

2. **Generate Planner Context**:
   - Run Repo2File with `--vibe` parameter
   - Copy Section 1 to Gemini in AI Studio

3. **Get Plan from Gemini**:
   - Receive structured plan with specific steps
   - Copy the plan output

4. **Generate Coder Context**:
   - Run Repo2File again with both `--vibe` and `--planner`
   - Copy Section 2 to Claude Code

5. **Execute with Claude**:
   - Reference specific anchors in your prompts
   - Let Claude implement the changes

6. **Iterate** (Coming Soon):
   - Test the changes
   - Prepare feedback package
   - Return to step 2 for next cycle

## Technical Implementation

### Action Blocks
The system uses structured action blocks for machine-readable insights:
- `CALL_GRAPH_NODE`: Function relationships
- `GIT_INSIGHT`: Version control information
- `TODO_ITEM`: Existing code tasks
- `PCA_NOTE`: Proactive context augmentation
- `CODE_QUALITY_METRIC`: Objective quality measures

### Performance Optimizations
- Intelligent token budget allocation between sections
- Cached processing for repeated operations
- Parallel analysis where possible

## Future Enhancements

1. **Interactive Manifest Explorer**: HTML view of the codebase structure
2. **AI Provider Integrations**: Direct API calls to Gemini/Claude
3. **Workflow Templates**: Pre-configured patterns for common tasks
4. **Collaborative Features**: Team-based vibe sharing and planning

## Conclusion

The Vibe Coder features in BetterRepo2File create a seamless bridge between high-level planning with Gemini and detailed implementation with Claude Code. By providing structured context, textual anchors, and iteration support, it significantly enhances the AI-assisted development workflow.


[[FILE_START: app/templates/index.html]]
File: app/templates/index.html
Language: Unknown
Size: 10,261 bytes | Tokens: 50
----------------------------------------
[Error reading file: GitInsight.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/objects/f0/8fe884e756839d70605e00665530bc6af1de07]]
File: .git/objects/f0/8fe884e756839d70605e00665530bc6af1de07
Language: Unknown
Size: 10,940 bytes | Tokens: 5,381
----------------------------------------
x}rI)P 8@]V"(ju
=dK 
Ppp</
RY@%+++++3+dRORLbiU]VwƋrjbvjlۢZn>̗E9&[E1j>]l-gq3474ϖg<޹s앳qqZdlZfeuÛ^?2O͓s׼BY_9YN"&Uw}uO菬7ϥ6rgϻ( 1k*_ղ@_?YȆ|QyP$ر$'%s3dUU݃;N%߹K|E.ϣDR/'	~YpsI^f>U?-;RO-P2;j˥H^.[~L,\t2UH
ez5I
XC/ۍoW)2jRba]>UQN*uzsΝOG|=:?K;NϽi1~>
 wc_'h}(y.i,fsW\]sX JN״]ifnLw
f}2 fT4gsK3\BJgeһH4 V98.Ҍr肯oM%ʙ]3O/̰7ƺoBz<Mʝht3*pY.
H&f-:#Fq/ȨfY9rw{n[0Y>hY,{${, |뿾}+,'@!VLʫI1[rdȗ"_jzRFyq881ʫrs
}1MG"@:>t+[lËdwdS{k|lW~1=KD=^~M`Ox`#Dk*+<˖:+W`,/.WT4[-3+fL-wvL.2/
DE|9}֮
K,X|W4*g'eCsR$8ZWaA\drĒXu&<M1NV#{16>~88}T'wkâE>)u􉽫jޛ_1%yiʒ˒T2P݁C|Q~鹢~l(X]5P9X/5t[Km8!rzُ9`2SMgQN&ITtT@(N|'+*dCiN,D`	$.|(wUw_,w86g4!V
$BW9z ʛZ-:Xm.u_HrLl8:@MTNXT(grq wS"H7CYXHd3&LiMMCUMl4/0w*hؘmzX*`T<5>v,vJz#*;)ߢ5I&FdQsQl62̔ֈ% Myc RA?lP#z
R6Rbd@w#?I*(~^V=?})YD-`nQu(U7XsnZ㚧r|_;&8T'PqogfOv ֞QeEAQ"Ǚ3I4ND&ت"fhh7Hs+rkx ñcn_1Sq	Hs̿s+gh-:*%mɑ
ڗa!ˏ5>:
Pk;pMˀ+Ƶ}bc[AgCv˜".,ns
VPj^h(`۾AhFEɧe@G=YiA1$X1x_Q
`ng%r|RYlDuIVay@&==tc s$}];+=n@MKJ7ւQ"t
62}GU^UPё
W>%U\j;\3K2#BeIf_ܦw*xII+whpriYP`D$2'1ɗSKw@asVQ7HY9/r=;KF0̠_v~׭?m=|[~67lvw\<ze\+	&7W.~_@`.'O΂Y@&C(m yfQtuĂϭ2s8[e2')	f3!_KcfY1^	*@+H5NWdDUzKĉHhuHu
]fZ1'9Ӣ@0-zڱVR64&*-V
$颬?)S|P,#P$3KׄTK4E|n6
eW퐥LK
8e2tcggTlo	%=@+t
E	pzSiMڿ+9iOsq˨:wt|^dheSUvmPF#ZKF~[ei!p?﫱"@قG+l\	%n"C+Aax={峊[ : 3f2a&X]B}w0]N=l+ϼ3QuX
޸'[B;Q?IRE%K6ktEu\BNh4-B14Zͩr}(j>n¥=jk?V>nA΃(~dI	(kaeƶT'^\	$9ꖨM6Rt{m/eRc8fiãY
Q!NzޱsB"[zZ}n 菽O5j=Pm,|td'U#jG\2tx[|BNQ-,OX9Vl~iɬ vu}P*	<(U,X0ŷʵ^^9wT;NsZgv6?0\ !ԔvE}7"qn*`]Ͱ%B;
~1j+wcV|ւUK_-GFjN$&jXbAt`h.XkVU11I &8LYDl&%8?
%1:hP̯dL
sKh[BsN+3r}22"xnGDOĦ)8|2x
wZ2a҈#M*
t$D7?=5T$;n%yK[- Bõ|e}wrbV9ȹM=#!;
` $:hw}U,͟/Յ|/<\w5D>ΘA</gZ豆|կ
Ɗm_B9W( E ~c^=0$؂[FHJcFk]2pK{LY'[⺰\ݠУ[/bk{$ǈ1{&a*7ZxS6j^z5kI7>z|z^<ÖB(ɮ?3g7namBײ dkiBlcV>ϬZ*ԑ}տ:ckK5@sӔm.j0d}rR mI~sR5i+5;^`i#ە/{MaB):	D9r0aJ:ocF<W5r;Lko`-ѻnk4/ t.yF	x^s+aR4}npW^t(/pqI8-u .:!RWtXN(ҵe
/ː1sI?FdרgKq	`t'E2so_PEe`	5!s1Gj{G~,dxZu\oHk݉li.vT<'BROaE>B@J`/XqoQ$achG2TX%<Gw6|#[4,bFGlfIԯxAXwaی
QÎhmm?lnaq !O9xqZ OU!)tҏY;y*G	[20?)x\%ეP|nXw"|M j1xP:zqK*tJ@~ߎqsLSQ|擡o	4y`uC!'nk1v3x%NQe5q[\℉oNz\ghFuWpe4꾹[tE	Z[2*6@&It:cα1K[8i6X%o~wZ@BnӮoU@X2
"vwUABݡNz9 `y*}+_++'zL֋֨8At^Y'WEouS%yW}+ʘBsWayn+ꝋ=-6FL]ge:< Nta;3GGbւ[˸PldPB%A!׆j#\L!T/|>c?/[_~o 2E?+}%zbi5
34q1r2=9_qހW$8p38+myϔiN.oNVg<$(u(iq٪ SqʠH:`Ra&.G!8o	<YbOq~K/Ihms:٦0Qr?N._F'a! U|1Կ䳯0)-1.qV.8p{h(Z -FϘŪNl5Z )`0db ]/	~?(@$9K	hȐ]>,p;qt1v짵㽹/-ȶI[2I4ptzm&~6մևȷ 3I))WmD79jҗZͶKQV5+u#m%cdE*| @VÒ-_~K Q:mAANPHR|TEG$EI1s<#{ųUOCDpfyjV#82ʴM@ɗ1-cyLH1/E_?4#BP.f5;IHGJձ'E?+ UXRhj@u *P.vwGYJ(ZD`$hī~p/MD!IZ<-A``)+<Z|rFMrlFǝMbY6c0EdrYU:˻#ج^t$}HAQ-
HMAJ5r_.pwzRfVR&7Vz.Ɲh(PM
!o|uiWX
=O,ծTdw٬ԂF4Lw/M$	(=lk# 0IYlsKrjȶ7kIOwq}:=l#M`ISu漿d.:vzpGwlp3og e IjREݟ܁
'b%M/8OPBu=2'~\,ӊXai-݇ߩ(l_
M5\DY˟tApbP3 Ջ'8Q$9qY	'3Mg\@Y%Q\Q[ezJ a\ s\0*EM,n5&,0+7`$EYSYp;oiKQ{;?/$99
g`h~{Y;^O:UO~;m?'pmΕop>6W\nT2![HlG_G{QkYlG|i%.Mʘ&Rg+`@t	>"%[HXsylѴcޑTOrZj&mOYu7l`Y`KFk\^vU ^-CYr\S|
\=Ϙ 8<Jsu l܁HPU[90 B&j%sC86r-[#\7!:hvʼU8}эzR``k~tMOFAoӦ=F-s	I'i΢yD΋AGtbMt;l C</9hzY-4<5T3'č!qt5\AP	G%vB{v
X'x=S)Ыu*QuvSep?KI0%uI~84"''y)[{55Դ4i|j
YG	Q(?g#Ak;3LZE @@LCZ/fz\-#Ud |P]oעNk``LiM*u+d6# z0R%{9\jzsCM0
c^C8G,
 @@y9
Fn/yf[hCr@cnOPGztm~@ץmc{<`\Np5Qۮ(b$/-~:\W%[*^K!3	@\4 '$zD]zDj[NV1k.tUt\DDwL%42i[
Z}r¡=mtcs174
F+\QZPHװ\w@pR%jE>VfvJ3
#~\K>,+cu#fdT]Ȼf׆P	rw7͗9TO+Y]Y&«R܅[\UYj9O)mj={F6#S1lP9x8Hxkl?OAxHn!{.7" $Hwgގv}%=Tn:G~ I@ZF{s0Ѣ!op1 hZбĄ9Gߐ	b\4k oNl+SY߉!ƑD.4 X6۩G,nnl迹7nr~s;<祱rxV'P
k&fq@[6Pāk6׃sP,VLD7xs92!)buVPOшnȨHkÙXAǢTH<^qp]X)Ugֻ'p>f25D#q*~[,\oiڊ MrwNwQ`TS\"gmԭ?nX\'fYQֱ uףdbmOrżp
K4IzcrՑk`ckyj :q{Eȍ=<dT=73P,OV"<Vo/Ô,7ic}&tT`kHnMm[	LcՕՒEÕ-<1^Tm={FtHr~LE _5ýØ첆-w^RjYAakH%i)T{c@CaT[#Ô(z!S
OB1;_/Y	pvEu"-t
hb#.Ddy˼%2KsMS$wޟ~D/62<gإ`iT k(&v	k)%GB~K	Ie\Tؘ%᎝[.}<'?^H}$?'ZLG3EYU,|mYM67TZN76ޒCnlHmj΄BɥyvnRT6ӨFxpRTD87eBCY -.Aw/q %sitv4xv)[T,~'#:S7-/s7&~Z1`{mfwGK|J7b0XK-UB1p\,M tZ1vh;-*MrtSCܒe-wK{ׄۧ>[x4A᪠99D|?,s=Ԃ(u-EЮ,!	vҰIkƗ8kC#U0p	Wb4ۍ;ۚu,	E*	P/VrC䆒5\6u
B4mLGl#|\f(P@xO!xmη<,B$TK-[.m-!ofؐiFqyJ9ӝ6#^8~TZv,v&ɹiI 3E'Hg,(<I wnbye) G['
ϏG!EX.ފE^mF4ޓAq2<N:?oSK$tu͋e$3# xzhn-rw!M}ϼ{@~j*?e;֌~'U:PRE&-`q1[@_NmX-Y'M?9/s#)%8@z2oJU[4dǴƛ,nȦCF:d3VSKq9OV
Nmh2֍uFaz}<շ<Ñғ(\x)c*qQ2d/yh%@.FJ]Ex_$^ɢa/jhspg	%R1D`81mtqϺY.xaD<Q'Ӷ9!"oRBb(jޔ`DoĄ-uW;g8?l\kwl9ߧ U.K2LGkQD; 9_-VƦRF$:RYO+^M&W0}HL;n+i3
	ђE-vZc6@zI7Ccx?qi6c5@~LyOKqG\*Bvo^F[k:AY㋫CynWU	Xy#Z2`85FAV\]):}(-#90uuK9%DAELoLXҕ&qZ%qf]޾Sa,>:tx27䚃h=Iy-
$s{ui%۾ }ApIj_QQk}};?#ͽ>=N;VA;v;m]vl`P"$k1
nRG*8l&gn{n)	yv
_\j5QpR+T$.@]߿u̠2IoL{ִKg}"|af	L=&oBh3q&J\t{3!H+ k&zspιQw㰭Xw>3D[Lyn7?`g׊W;,Xfh5\d<IzKC܊(? `=ŲC(?TaQ<Ҝ֑@yWaʐVKû!/ۅќ\#xBw?5BGψ:qvtE-{Fp## !!* o$ʫ sD{b^Z2fa.ZN,?1
\dM%IEߎ}Uq{d_}lKG	G7F$'8ٴ^M|%\0U	kg.Ё
\ޔY1$Py
7|%[<%G{Wȼ`M";∎zȼTpTϮJaEc$;Y%<*!	J@@0A<mDT%\|C4mf4	Q)zwM\hǰi|÷Je_З
<R##&L,&"@P͑7U&Wˇu5lвUĸ~툺
?/#m5#0uՎ(dL୴pD3"Ϋ1P؞;сi`l:
p.l(Af8?VK-


[[FILE_START: .git/objects/d1/144c642ea4debfd3e751e1089e0a4e9437622c]]
File: .git/objects/d1/144c642ea4debfd3e751e1089e0a4e9437622c
Language: Unknown
Size: 11,150 bytes | Tokens: 5,593
----------------------------------------
x}vGrnSL Ik/"EG6q ,ȑ 23H<y.OrHʛ]]]]]U]Us>ϓg~X[[{~Z|Qet"/*/nQ>/i6VY>O>ge^GUR9/U6xT!P4N|8)rp|5 xeG6-J~+o׏e>ò_~l9EҲ2ɰLfG"%͂%YYm$')yr#ytF.4;-StXiidӱq2
ѥ9'ud"
UIȪeQ7Y
lE::-1Qs93J]ÒcxqzY$eY2|%gs^놅GZ",~t o䣌Iv,Mؤ|p_4Mߣ?^z"Rwz$ȜO'4˴c*w^zF?#2%{GGo_}s%k~ys6It98<t{k|X3^dJ<~#P<_~ނc-泯TfAL?# 4%AYNvz7z>S XpMsz/3,B6;X+|SJ
^z-Od0oÅ=NwƿeR78|^`%l1[<+^eZ'Li\U:|~'^=9j/n0!EشXfgfγԆr=̲y_G%'XJ<h{䔽o/;=x18;==x'LїNtb=Ӈ!jE柴"Q>MΗIZA.տdr8MN8 εdtD[KZ=/ټL^8A_Tf_N Ʃy0tP
Mu	%)mF֚zoPįh^Wb0$UYE k3'/ëw~Ӌl>ME3p	|t5:.UR^)
&|4'$QfW^_>ʻG1?RU],i\wJ&"m70>!!Ta,"eV3(޲g:8|dd
莼	foBE1nY޵E>
(@&v^k}^:R˳j6[ǐi)C=~JmA
r=m ^au兊ExQFi.ٰc몂d>@G'޽؜>nP7bcu㛀<<WLs 7੔9(\t2
,i:}UiQ'y116|$Z+,JpGLYӁU!%%hUSɯ@j֟-sR6.pz	M%3@&қ|bOhHU'|7}/Ȁ%9Zw #
*6A-2n)aPؤ0tgQI~h
&|`ݴƄw>a|vs~t`էddg0/w./KEtd`=WSXkrL |Q{ƎSDr#0FEE-	2p<F؆u蹠
`p/lI-MU-d#BRˮ2_.C}s7UX7^7 #vHe*h}iIsipM@hEl
	D!tR`ZvO±!9{f8_E],U:0@C^GY2ȸT@oNEUE%]Gt*'`AiX~hR׬hdU`pTR'̧A u[XvV3o~9z?߭c3\0U.zoh}_O#Y|5QS j
O	А'k="9nl0UZRՙ'k2O2˴JD!.v2D:p=8M*|8y_Bo5e"FgsL,'qD/
"ow[*hĆTVD]8޵>uzccG%l(!0W6U748j+vzkX
YP f :z5_1wIe9YEOaB
Sz0;]T~`+kesRO}w='(_ 9FSNݿL$+Em^娮qvh{WYD~pmA;<U[4ꉍSq8)s<Afy
^66"Rk'P:*2^~Gd<{-{'$g
4H!p2lQPk_>UiКYtN[UfNwt8'4u? r`\\Xo*tU	-D 
8QpEoX9^c v=m0cI{v01B{/2͜<ڰ6ԗ5dȸqseIR*[[I b2@T
]yG`ޏ4}9fE b
m{Bta65ENZ7i]:ԭrg1ݥ?֛h77 UaWsGՂz~?wHI)l^obE|_
C
!57JDiO$"g'Oɶ찹ޑmdXl8D

]vdGx!_:e/ h.'p~oM+x)zڢd<#{"Qq^	M!KN}Q_~V)z^$NIFۤ&+LS@SR%kDm.	*nP 7!	Cf';-?|Ɇp@/'D
Z )oמPR|^%ФUe=LD[sMǕFI.Ҧ춴o"İUeTX)ت qOӆD>.[bf4RɁ8717^mSd퀢))i1JQv-jӜSjL$[`t@h@Qq`:AQxodRz.eX=^P-Ce4%8M6#*t)+?&ɆD9hzO]-b.^臗PtYmv`?4zdؖ7Lw}-b}sA02Ɓt${D|-Lc!E<L

Hg
'J2vm {zk!4L|dA۝W0{\JB@҈g)[]Wua&6pHR!!CĩN˙aN]Hh *S{Tb
jysv"CЊ~la5Vd70Ŷ;jvhŨZ(}1R(:}g'Rq>RKi-/v0S9@O%R*$9-clxH@3*FDvz@
Y0.w8a<FƬ.Ң*vh?a.W#ݤ~o	P0M3{q$v>\?qU`A dLl~I Xm,-e}]\&!0]|)|
t
jċ9
R  ~aǍ?mloml?~@U紻utk#ٺ:\'_e \s487[ģrdc=xBgĵi0qӸN[]WVHȸ}u;w)[fJm:@Ae0qHȊYT5.l:hQ=p8-uGcj@)QcI}G8d9K7:&Au*Xj`e>?"ILF]EhT++..	3'*\W!ĕ.d*g ÏZ6Ip@]׈%@Tedth%l1ӱϯR$nm_ؙD 5Ew
`\0{HXe4e,JGﱹqq͊n-u]YuFmQrd[kVPUF-zyYAM²Z`kEQ~ʹ$w#*i9!9'n J,2h`Q[)xN{;XȑOwqcvjf*µǎM
eR_ۖ+ӴכY>uJL:M KV
;&-zo&Qy'h$-1h,0
TB,b;Bah跓-b|qF[!1luctf 5m#c[It
4b9KBԆ-ngEpbqg#72dOh>0DdbV7SoJ0lĦ#FXF?8Չ
j7]Xx0"{<ǙDJSh%f<"0l90 M!E!!:Q	"-z$jJ
M氾ux#^(]!ܙMJ
%aԡ;=Ćԓ3'ᳵ
HJG"fdL7rcZhsH*j\V24mUs 
m(}l3]Ua?ص)ăj"7=SɴcnNjǽH.š$u:#6eZKu\(bW7SIa'G6l ~=b`O.a@0ATj8y+Qf4pqkURX!mxF5WFزՎo X7և9A}l H;dpS*zǱg/	 &_XY?fZpt
cQ|Oq#sO+D?<	JKP
'JU\"fj;"R<A/Yp\7d"tV!&}!QyUZozJG&J|ղ3gYJtujF|}A߅ݫFDr=[)ݠ[}y<i>h1dY=ը 敔6]La`2b Cωd!j62Y0zI//f}QA40oDvё[l^-@/8(5pS ~k]t+CHuA{~V6CIjյ$1j:Q5{N2<.<0ܑiսpp:*@	݋ZJ=8ƦƝoI(a=F(	ꨪtt21|AT5"C$}yX11r1&	~Q5r^+;G)|J;Em:;XI]fsWb%1qlDt2BdŉV_BfLD=Dl-bn4\CIG77^_;aH8?~b
#RhCʹAW='0*m1Go|Cv_/o/c_/	'
+۳5
9C/3O)A${ln225ђ(ON-]ʳ#TN8a:U:#WFg
*e%]4'&|^S鍁޿g$c74;;r`?@Lm
;^9uǎ꫕i-RCtVJZkp!t2%VlJjAƯiK´hZ0 yNҩ I۠r@uiQ`>}4${$H@S ;Ђ{US\@IŖA䷿L+(8c#؉MҵL;'3$ۃǸ&`xE^2Q*te@MVN*9d&N4gT[ـA1-Qt~$)2fX48J֙HawV^"\9-$6TӴS<*ΐQ:6\䵹2B < 䪵ČeQ@.S;~J9w,YTvbZM<QUgv>ǈ	Z7yQ]`B;`V+ZqY~6*)"P)pkIL"IחbpG7{\[vӡju\<`N2=*ӊhTi\CzQ.$tGڥBAMЀTލ:V!>7F7
/obK|MDa#ѤXǄ
\e9'ʹܻiڬK~{Z zL}nJ>9`oXRbX7q)R
`˫tZQ8°n\G1}"e׆d_b.wl1f2j6nN_OnRGOaGrD&iPƨ&NJ86|Kة:)^q<"S\Wt_l4b~h9JgVɆHlWU
ad(]fhSٴW}2Nn<qplu(j}/[/ivX [a.	kyZxxЮHB;U6V+s&eaۘ I6B=WwC/PpEsBjxWǷq,)MWm`/]Xq
}.E7fc-`@lMϓ=\7ᔼX
n?;;&B.MD;g+pzw	6rO9` >#$±-W+2,M{H!ӓ#ꜥ*gWOHXߘtunoqsay$T*6x!~Hpq'}"2JZu5O펷m2*Q"7#z3*zlptf U&Nrܮʛ%S\RW 6qm{ƷPCN_nt#aOx  gS9: 
a"R$BNw߇@'8-X\Ų
  kpK@1ܥPC(oqV@mG'M
2SF!3ۚRoG[Gf?G8FmP=VyQMF }Y.vB6֤'{:5mVƔ܁உHc#T79\h&[V8b>ѐխP2Ibִugt=uꇡqb'C&B<a0@;eL5I\GӠXWLsM,F{%8|`v
12Skؠ5Vxk<J$8$p>ˡت[d
50?vڪQ H`$8H=Ų;0rU3ѯÓgAaHUbJ)ʴբm&˃oenjpOQ)s#mB^l|Jx= -6DfQՎcKl <*}mT_z3z^ŅhK^-ֈ_`p2dW٘ŋ$rlr22S^]	e69PF:Ԅw}b*U<:z]ֹ?=/(5]3cgW
˄"|Gb}xE'*7͗C(uVD+A37ڽ׬fT e7vTՔ˨~}xYb9N!G|=ZtrdKg!Aj(eX:N1k%vF&ZTcGcGNdƂ"6t;渍0x'8b|qf\8`x d6אThckMT&X龃 w\T1s-}їx~I쇋yX4YޝȰƴ32AEdĝ"ȾgI Y8JkPX Xq[c5jސͭCVXO޶6۪֧|^=nmi}OkW0Պhe+_q=nmCDf	i!pΕ@g}!fv	d/]DxPxۺ16{́Erp-E&>Ct|_B;-%8LP
ii!̯4JCvzlpN*j!6 tuq!NlY7qד{cԈ `Rg.nKa8V?4"f6 6bldJOw[.N^{-+FȃE2Dr4mlR<͕ȳ|'f7F?RUX:NeM%ohxsu!`$qC.&< 1SݥBۓY ?'aB;Bףs`ŋ<xx]h)8
'Gk/2"7@7wD4oWBrLpǆ(j+8ٔ#|,d}Mv}ycϼQsMfb/bٰh+b]F-,KTT{I8j5ijDt|!k
tGso8͇,vW4/`ʰPC~2s0-p{pZgA@)8'WbK%{g"wu7?|sIg.HI0|nϿGCY'e@]9WYye)kI,;=>;nBhZgr%d	.>^
C ks1%08Y@#-H(HʇUw{ݠ,#z+!G<Ǡ_h#
)BI]SD34Q1"xHvKv<.܃EIC7ymSǘ0^ep[XJ^Q@#P]@ ;)5 >i"AtכDX-vcdfNQ r%Aݰq 
0ݪw[ Y.%SP]"z*ETל5_h	7p*9ɪL-xpvih
1񐢾>e|#V! h>An&x5ow79$(G?`/2zaY#zl`F3jeI\	wBL5;Nvv.Rn뗼>lHj&GC"xj[*;K:4܌=CR./ݛ0txC&H&[>RV2Xu:=F"[Tq UTPI%ֺE;iM.`EĂbUrel
q"ɛ]qKr$[5+:WVovX`+:,OeD]䟙s!YF'"|,$
iȉlB/doe⃘{Y7p!݊՚J vҕo'Sְ	Zb@
ej?E(W&3`G<mVdMb:țmoW3cˏ֞0bXlցa
V\.n`]F+=.3g<=i&_@cs8pg7Ƕ\`s7玲`d֝Ww
n)k3Wsd3_V ]hGL)=h5t~c'wj#g?:jh<wKg@*7
QDyJI١.pMRe%e5^ë֓g~^3ougK9ɸй9cDpϒ>SkC
s}_<KMIL޾8xMKׯtbyI._ޜJSa|8nb;: y%MG7\WuܵUgk$ŻgyI_A!
](4doޓ
'ĦV6D-t
$<-;D7;_t5 }V*q71vF:OMrqB̍;r;q%5,k2{ͧk&T88{t \=x˃S_U
bF	-y&H~
2@$H 쨐ykDd;`[lȕcIx].&OY_Ww3Qp:~$}5I\e$*GD;ApvorH
MB\`54> r%zW0b
6 -;NF
WSpċoXQ}_pg	bv=z.LyG(kx/	 F6Vx5)?!#S


[[FILE_START: app/static/css/styles.css]]
File: app/static/css/styles.css
Language: Unknown
Size: 16,758 bytes | Tokens: 50
----------------------------------------
[Error reading file: GitInsight.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: .git/objects/70/40c005cb683930d392b795fef38d57227cb687]]
File: .git/objects/70/40c005cb683930d392b795fef38d57227cb687
Language: Unknown
Size: 16,992 bytes | Tokens: 8,476
----------------------------------------
x}r9^)j hQ;On-9l"RwX,WsOwd/H UEvFUD"3H iwuxbRE>ri9M<˯e]S|^Ml^Ox igi|]Yxٟ xE^vb2-٬O=RΦ>_."O՞'/f,L/h1d9S\UrOhXd/ޏWq=^kyy>.N}#?2/GKFE>zGI98|rk$(gXBV|VB6_"fU>X@7MІenK޽+G"%(3
WcdboЃ|a0񍦁@|{K0IGʼ@?c#MGjCnZM{/}x};ǃ^pp=;}߽^;$$oogVxTޠ?8[.zg}B߱7eLuOo_eoZ٧V>g=˼&tP{TovB'owOσ'փcςXAI?! _,bwm,8!ݐ#_}:ヷ_6/3Rs}'pVt.[^jb0k̇y8H^qj|Ee'cX2P^c0Sus}_'VB-{9ς\7c2"?/oO.hG\R[<s?F^xКϯ0km4Egț4ؕj[K%S
9h5:(8(aP $%9هz?=xe;aԼhu9˧9H>>_%,yOܙ_7h1[qvEU18QKQr5,fPa%//Ŵ^<A_T._C,sCwPz.V-ezNj|od<`4ͯ>hmeY,xg beНlݡ\_՛et
<当&jSbY1!+Y1`8ݫW/z}ɕw^9L觖{Y2*z\\R<_C8R	R5ĜɀX**
99yhYڄEȼYk>tBM/g|vge޹fzj?KH>fUS4]iH	mEVI
t
 kPѡ(0ʤj2/,ŸZflf_xٻW?vǠ5꺿v"d':"|/זuk)
x*%|B:w'S}gR\sg/l11)":9Vrb_@v)yv^@P. & 1sR/!J0edkx	3ǩ}gVܱm4+[*=E"(-tX~Fv
Ҧu#h)֘;P /{7K Dt;^r	˛}BSkEfTS3P1A-e ͯ=>8cq1}1퀦``\lsh2s0 bwg*1,ZLF	JbӬu?ƥ4ɶqB OBJʷp~cp?a1[͝8Ά\3/aL}	N{V-IVgφ??ʀHl="͇DmbH@-#F[ك0< \CviMlӋ)}hQ@^gӳ%oo*c~.lqQ
h2+5,?%kP?-w
zO]U
Ʋ0j
jl1߷4Ƴ"3iWryCclZP
g1!,$zVtMP,^PG*AXQZ-W}ݭ&R NG 3,YN* 7S݀$=Jyv
ˇҁn@v0TΖpRӕL?Ã	:jCU-)	[fesV9#ן<@;sqIKX`vN[{ܲrAd\>"z
e:=׵'Wm
k.u[{ 9 QGoaBJt=)~6vGP"ORn 4Fe5TxVew>5|ya=/Ǟ_c`,BJkk	mR׵,j_Zz	,2YߛQ'߀Texe*ph"3LC1o>JxuN\Vo%lP$X/bd..o
0'o#CmApJ`SMU<ZMXu4BwL퓯urb1ILX/Q[֬&l:iբ(x>*G/=vbj74{)_yZٖek>S

NҊه2f,|XW1_6\g|u)DeRܿjG']Tb2/0qZ>Whc0ى{TN
YPVY[=,ώ^5kqGfEUi#XI'rs!Nf$%Xdn
P-I
]d)ڰL ],7 ܉2VdiFJ\#@fa^D2tr5	M0jlT(R&/( n))?u)[[<;# lSrr$Iٞ(JL^PĠ܆Vԅw}`Mu]54.w=$Uxg⇹j/4iLq::
D?tnhRs{@K?c'k,0`2}9I]t8\A@Y@ʈe!98HzjdT$t'dy V ~O2SK'rxfGL|W|E
Ηr
sRX&|q1ĜੇWUP>RٟgI{Rd&EA`:#y>4BIgU-A,^+6?/
%;Ơc*XBƑp-Q:)Xom=pLR&Wg[r/XAT~ú4$+&X\zu޻
k
ys0fDk}O3MƏ
K5Rm:Ša#yZ8ŚXUj\1[0yRy4XR@n.;XҵJSFŕp2Cr7v_烋HQVubh5tMާ`h"4嘓NX !)Qޚ&?nYHq NA>!K/C%V=Eң;K.+[M?VCIne11[|/iiUDEdnYl~v(Z\=е	,ebF:Dk=+E)3CuǨ,Z2a^C"DɊ1
qAksfޅOUnmyj0WLlWAvР~t]%!,V5OO!l2`xJ`AD(pjr}Kx 	OW|Q)*oEDXq_5)T4|=4@;I۬%i e|jp5,o'c.9roR<ϔtcURJ_HA>`*3)L}Z;A@R@MFtDKrt}f9i$ 
O9$:=ED,
Y7iBn.C*$q~{M~tdZAd^:;z4D6ln.J%poO1UNF&@?1a׿.eBL*2H8Վ[zeiمћKIjU= qp<{1E崧P0q/
"X@r(iu7JY*G	
iܥb1G]M43ijJuVCb]V,{eaU t9@{Jξܗj)nc")%$-V=rb"ܧXa&*p疟z/.cTWxؿ٣η=FHC'bxN\]"}|Z:Ods%5LN`ІWlxvnzoRnPC<!xrx_\]Z 
h 
qP*+}C6
TALET$HxXQ2{#"x		^@ZY
> `Eeb{$p?>8GQoLG81*Z4Ihv<ܹh}Č
[[FHeigV ߁`v/",|Dla07b:fd~
E#P)vU<`m6(Ē=6?dΙF2jp5f*
m0AuYL@eW;Y(JfL.PY4XI]<%?6KިV &p8/)	#	z?fԊs}uo&X`LAeWDHg7FLk 
LHf^5r!Dc>_VkChMxx7gcu)mno$y"BC~X
o*B1nm2jQ\MHvW:^CC0-:"0Z;|2h)P;LViO7/H }TRPO,
7ou-ilbdAXKDD&4C fa;yC',c-4`'b:հNL	k>`Itc/s.NAtaBw*bLw/$jqUȴ8"0Ӎؓy\g1"^PȻ׍Qi& $ncՊҬvh7]CELlUÃZ.4B'g>K3$9 ΓZ2y ud+K^:Lq0ƬM%.GwA	jdg8gmK⽬d'ƃy*
ֵ#/iouVn.1e5ZJ4«KY8aHC5*STZZLȏ0!Q84o8Dm7%&dG\(m	)(p"&7VjħnXN{NUcF0lmR]X*mg_!XQEQd\Wl4 AwPRb+ˍ&R	xhU* N:T4웴82@4b?JuU%c1WwIDfT-6
{6WLƩ Z0/3~s	q~ПbaMYN/jS"0ch"eLkZ7%ƾ=/gV5lO=μCN.Fߴ`A=͚l$4ؘN%
Yv{
 ̫4:|,X2]ռ29SJkw%GA\NV>ѭ@߯DK06	0bx):}PՒLb ;g8\*w@csDu־v,Mh$5M-LT>W^)i:[MNY(M<c_L)H{ _zv~w]f0dHl@H'HRĬ!.'E")w#@Qr&tzJieISGH_	!yOkj%uo;ܴi{LrJ_UG*g坧Jl{Z}
ZR;1WB;%(EzbCRƭg%l z"C.s1$̙=Yຆl{y6{R>X'f@Z-GǄ3(;:!m^Ы/&oWnfҞؓ 6_kM%6)ҌJU?X1VRŽz>jB( vtVYz"y㌮JMr	BPq?z'HhV=A1%됄)V[d'{
0q"^&ĤbH84SNե|fYGU.P:%4vW3
aBŖxE(B(pU	ƕno;uKM@oȨFMvD1o_ʢn|A |6FS̜k/b
ǹVYkXEvu@!SN_LEx}yu#_ՄB˶)8޽_P}Q|xHS1SP_X"䩭ȶCL6C*bk
$ +8"A0wn,ֲ'q!\"ec|ߺee@t1
5}(l>ٝXGVQ#H.t uqLf
,uvFGGtF3op{;HBqröRCJnm
IA:(%hobޤ,[qcBO+?aŉC0(esH(;P=h!!5;ep7
|XgL(ێ
t
 2]PFLABMOl&hff QZ'!ʴjaV=8e8Gf;6erةj٬nt:c?O)/ u \*F4D{y@N~/<T wNBaU)_daE lSduVl/x:!-G_ă~C9-A3iBGo[Skmcic+?\ ?~)Jz#<C'>/3I2?Nl3AԦ9.}=~v;ơm8黝ag㝽';̎egyGX1~kc]}7IG3Q9
pR/Lʑ4H	D{}{q<O`0Q17):͏r!;ͣ[5|
϶5@fAe0^sf. /9'3eZRF:PwM>	)M%#UئƐr39+]d(We Fco;UB=\$6e27+2f$Ev.X`=QT曻eQ3˿hRLl+N0iK ֖M VX2hw1i<U[\\x12
agb4/9&ƕCAX5,(ZI]*>Sse籄zFKQ^Kgn(Odz|jzMZ{%[5CWž_$Nd>wTɜLv}$1P
|z67@qm?3wl$JFe%)>k,P,sP=jm!Gz>}ʠn˿Ʉq!Y+M{ѐג{&
}J5s?]jrS^ThT	"qr̰Q8U)qmT"JH6*ǅlzTt,:mB51=
aC+E?O" f9#?8/XMMލ_$Z9YAkdrOYas3 V>h(*J^;R'溺Ԑ5!wz͚(,V"QN ܶCE'zfe<;; sN,îĻE
\,nI$F#qKhi_OpA-V$u8ʅVmbKeqcǈcˤ֘TW>ny4ENeJR'bI	n\Ã
(T
`{i%(;5sX7ql*iK0Չu%oX5՘ X1h8D'ϷF[]]KdY8ߪ!֙g2׎[ܤؕckja>2#֨G.()GCjB|pܣQc^.5/H+&:rϵX?y VJQL˼ob0蚴x&x|n:e,4#Ճ2rM+À`2F<~zZ]ᦡjH MOOR&rVG3pui%+.mp.Bd'uw:"G%T¶o1|I a93Mʴ
vߧ
:Hq$B,\XULI^	whHJ1oA_;/t#n$t'.H2b	ZUpJE4hٓһ`9E'JN`~Zjŉ8x
;`U0%MC.jNLHIP砯FBjz
UBXVZ{#Vq/NpZeC{Y{ r[)T
,=5| F/~v:Z'd3ME~Vmeߵ¨a|4	;hni!$8{+!>ƇЋ@-LΖNy`VzL$F^pBr j-}8T,vB*oHM UM;͗FCCډĠ|$`bw4D68WgUZdpč%v@0	&i5,*AC/Xe,*iP2դէvav@MĖ%iuI$jی0cR$!OXywS&idS63krQE㊟N1?{H;k_у;b/c`kkLQ\
Q55G=sõC^o(L9YPb2Ϙw[_b-Gҵe5_d.V9"<Jl@u"bI,¶6!C#Dt\;d *t{=T/cERKmɎʥ 7+nc61]SzU1="	@Ƨm*`jbfU[TG|&estHS>hTƟ,Vznh!]0$[}.b^K*c?ym(0@S t0v'"EF"k~6;ޫ\p%OZ^
G*-t|+
+&J^*4ǌ/T~D"s8-+ae(ƴ'?Y9ܞk@Wqz+A4)5އ'+
P<EpqiUVRΞT)/i*z3B$ŵ}pa52R3F*Lƥ7zѹwD=FnrʒN&,o>,l5DEg0dvP$A.s
dJc Wfxl]`_IBFwvw
+)ڭ#	aZk[D}C%
@gַ3u-qW#_PIڨ16bAK$ܑ`)oݞP;SG>\koVL=K5P҄2uNdXˏg!MZBfE &XLJ1~ZSa|	eZ
4㾶7%gT4#|`vc^HJTt4:0 'FVź݌̈,@k #^9*v0xqtWYlͭveu#۴~i
09 ;e1j
zNp|NKz}Nl>s{wD6v![(^{ 6wa2aˆ^_E`_ H<MevKEqW[Rjd)\DLCՎ3ʈ:Fl`5;AV)%Bި#Ύ|U\af/亢ĖP'KH|Bd¼`PlH;}֣qhݞx%YJƿFaVQ
oɅYb7yAəڪP"\\-]2&F,-ч)"丳1r1	ӻ8qz7=)
Kt u5Eu7 Ճ8ӵR?.J@wqrKB94!%858)`ARGg[,jMBRfxgB@~"i N=wGrT%eAֆqpВ'`8"@
-T1*)Zdtx{6+<4Ngڃlc%+%.uڤg4V->C}/禌^)ftbXW'ug)96RGWU#2x	ynRD8U.2؉n"%n&ڍ&

f ӋW2=InNº&L_{vHlz4(vnMҁ
1f?So@2nU]Qxm=z+pO5>:%up_LL\TVXVŪWc	z,sx[~k|Wk_їd>˱ꮶ#phvrRq:_ًLN/G݊qsm_mn%7tȵ|icFC/p0%:2mV5b0-E.J
{b5܄{ wq&˓5&M]}a$ʫ	2wZ0\qjKoexaoĢtsgm1X'ɊKV\c6":j4Oϰj9G%yΣdpf&T4VQ "ϕݻe
h5i:|n.[	MOb=z^WA M<5QV hBiMmIԭloaFĝBq]Gscma]zľq:Rm紣-*_><p܍ixg$ub$`D6mȲ>=xmwEk&']͞"g5S
U>MG9Od(4OVq*pkIjRL"M*!O0OWVEj˞1Ru)CSbBȣ|R=5 dVD-KÝ]wq-/xml2ƀQ\5,?w-S-~վrGc;%ϟݩ3?hRu\gΕCg} @?/܇.?2nuz2Z^	n/HՖ^0	5v7+q%Ǖmw>~Łmr_GlХSNV¬gf0f!)w
TIg:v(Gt)i7eC+(_d,젔ԏp'W
ISiP"F]:7iV=izP,KWGJd5zl+{Z%9"]\|dp3 
ǟ
E/ubE* ፸SmwS8
G
Vy`[5ag{gXk8Z4@04Wq wVHnz;@!*c,)u[m`/rI붼#@	f<y((~p!+Wg]J>82wpID)bW1e_[>8=~Q'#z	N/ғ*yAgG"RHdo!v.ep|lZVfv
{KH#ꨅ;WP\uEx?-yT(㮝kCbG͊]w`F7)xQ?6~l5L(Qq'&E<-zsO6+.'CWXnW*q	p(npANoI˿§sЦRFkWsܜӖT|aE7qCV`'4E䌈";dK}+KA	.-+=hDHN|{"Z;\@U=RB鴴~D?s_mQ0!Wf'F[<dW+6fnlʏDj	Y75Y
mn^,VGk>a!'A*I7 0.O/ [rϞ]-$VO.,@(k=3\q̓a8ЛA$'σd`{[K]\5V^umzr~nɸ#)˔fvKEnt$A06;Nv-Cwx::|tqÿѩFĹxR=`(@@߿XrRٶCۍF<eeHi N[ιiE<FFKp+!׌3q3h)C*[ȹM٭H]=D٩j2g"kmMmS_=cyaP?ZӊjcP37x^	uG%\ї@j<]Րݲdr(6
18 ue
1m
8<
g9 T<">sg--'bq̸v\T85q^NN!Ψ6M"SG#x3ep͚-
"uɡ[*)0BB]2M	
8 G)čPU
q_Ȇ+^?8Ѹ: E.ܪW&CJHlrQ
?@17ⴳ7hE'G *embKM/`(Zp7\Vkl!*8kL[OP<$g(-ŋ%$٤
qͤ[&#(6m=2sŽS 7)N*s,&k9WdmcUFJ:c뾚-٧XdeD¹3Vx
q*SQ,$yX&G,eMV'դ||JM1pEKy%PIj!Asuk-8`kGkWl4L?p9U 8LG z
;iH<bhG[gA/%~Ӌ)jmｆt [>C7@vkwA[k[-AP@bq:}VB h.7?t_TQڿ$y
b^*'\ޭȰxi``[@qNd_mN YkwרҠX orYْe}tTwԀ4Ԣ3&,Q_=O	7M(*ue5Ýd9ǉ6>&jdu5uQ=F_
T
<_[8
zϰ%
ǋ޸YrR.nX:4w=-Vw#kd?*+O1fy(?/#]pgDjuH*|3ʛTz^tH ]EobV_xg],)!WƑ׍ytkD)vΰGloY{M1S2is.xcVwQ\XPma9!-tEV+GɟS)Uw+1xdk#qf8^)~J]& "ڲYmne
9>aoВȑX0	Jb
~<e"4Q&Hg_D鮙K:ʓ0J@bċSL;3	}{i#
CtvBBnzGnXjлXX[w[^c\ePM։z]G`uE12	ۇ=|{T:3ҿbDV^nuXz
k{p'ga^<**Ŗ6sV\v:`ڻM!04.+vP׭5K&:"WpFt`3tglU%4L[,q?01[^- JٱRmFsF[_uW?f*#5lA
@\JlESʗ2y}b/̣clQI<t(ګurI\4k4gH[[l88a6jp@R> YCdNR!'6V!p
fPT9EECeVp'f	){G"0oGQTGxaw$ܫ;7/
*HrHZ36f6-B#*@@2_KNfs49F
5zz;DY-༶rBxSo)3BIvJA]?6ܘ7E]+N2;bbu!.5+[fY
@Eo5͒(k#jB*[zamA=/O}>F1n/=D -9zye_#\/1#CIr{ᢘ|;`vl--|Ʀ5ZV=WY0omVfn]} &I1\SaJ޷̢k
r}r [qm0tGnBm|($
ʄħZ=F[kwkTI^G):uV0IV$w{
 DrMq"Y)ܤQM݁jK*W
vJRJ011UbU%\O[鱬$\B_KNb1-@&Fr/.{'oK
iQq1![}X
jZ#NR:'N[&\\Qq9p7)vCXMh
pKjxHuٽoWh6><bZ^I SP`u|e>}aX,3m`lVܴ2/)zc[n"R @󌄨y ?pn?=wbb7,jAHn	 I2St?%ڨ\^~{P۠w4@vH[<HeԬ%"WSp{!1K r;c$[=[n!ʈ{xڙ_g4)}GB'}u1څIeke'eAk_~Gn"s.Qgg7@~ӏoJ`0׼7}7CΪrP͎{e4L{]sYuY,{.=`%<!k
<ԒX4tЈcy90)7c.Դ|xT5PW#k7%+sHk#Ǡ5Ӄ>|Se=y8&jԌM;bj>At{h=g-B.zx
8llD6؀n?nUJW-cG2B4ḄVHuzxs|.n@xFVs[){2{?8dtK^(<}D .THD)٨PO>('ez($ϲ
+ԫcB~Ɗ&
*	v+gH^T7GDś_YF!ϋN]8"-uee[J:7iI<Qk:b+gqZ hXqdlZ.bݟF6*&ꑿ!D?a>XA|.!o߮EpK*m"$."@Sam[ydߞY
d:|O$(I{a


[[FILE_START: .git/objects/81/ed4d7247a0f452e19f8227b3940cb28167ce13]]
File: .git/objects/81/ed4d7247a0f452e19f8227b3940cb28167ce13
Language: Unknown
Size: 17,334 bytes | Tokens: 8,648
----------------------------------------
x}r9SA-і==Ũȶ/
Ksf
E%x;,Rګ}Owd/H UEgFUD"L gYvlll<8Z̻b8y>t~b:t}..[de>d1o=(q=$;na~_u'= rv8MlZ)-q'jh1ͧ(L-`>gS\Uob+;{v
,OQOn଻
|#u"/GK|8&w_@HQϰ^
Y"ɢ5X
|}'?NGyoNo:F-؆f,x_AvUķ/<~#k(G}1˹i6)<8sw_:8?t^$Ru1qh9.|oG?r(;/t^ws~~8->7	8<Foe[䍭1^w
|y{z?k~:~>kϷ}B4b4ꎻ_Tx8n-Q_G [}񗗻w誃;9xwZIia`p ?g3y8J3{ӆ֬Ӟky&fI_$h_kV4 
<ugZw?llEw.y?g>;3g&Wx1=W{5/`E\B[<u?M^xК)n0m4Eߧgț4ؕk[
JK:N$7 .jcsA	\ ()Ow^;rsrrA-5G?I)n:4WJ:O;?f7M?Ot-|^DUbxZXeX,xPXK9_<w"{ }UpZtrϭNAYG7Lh&(qR{$I~9~@k,ː,R @Lsg>]&`w?w?`ԛo':.1N\iBI-..GP%F7hN
'de?2+l?xo:Dr˷qp/B{[\Go|wXJ{6_ޢBBp 12 /|)h
3r/d: -t0k>ftܺ5.ox?-
USx+\Au/0Α>GЦ^|je@K@/0sOF6XݹW=t
# oxʽc{XnI)Blo"̦b~c\ٻPj߀RR`n_cɽ;>YQ<=|LcIj]^"3cA^,^8w$igCyb؃J'3@F
Up
Ny4|4R
넻6Hqf߮3m*JM@`XKJ5
,yO:Ib7#;xy
i8XTkMvo(]~m˅v>!ih})"+	sՐþD0 944w؛eiƲ308,} dLFȔbn}xBC g˅l4N<3̸ƺ[0;BhIHIvjo-fMg7YǕc)-'sKS_;1mJҦ~*_
O">[H!5Ѧ~S?4;佃RUsd`c;{GXp$ehlCrolւ;!Ho7ݠ%ogu_&;w,e:4W?
lnn@d q0+Q>q]Tn*zè.WKhk<boiDfR-*<l945?]Bǂ oV˒lkjYё7FE06R<vjуnb:R	ƪrv9I'v`8Β夒x#>C%ON`Way_:

8(v"NCNeRUi&ÖyЄ"P9KKAF98%o̱:Y-=IQ^nY :.Oc=Erh+r讆߸6@eo5ZP<-rO2كuҚiP
&ȵUyrK6z(-o<qX`KHaJJ\)JUotd)-Xe J}n=ʶP	&UP gIfXGb(qZ݀0FA5S}`JOP`$n;T|3}!R.=TQ(
&,՜ˉ(+|VB5F}UPT6NoVA,Z6= R=	ie5Ζ2SLkڅGC+ÿSD_jQ^,4Tb=nj(7TXV7<-tK2拶V]a`kwiEpcDUP>.ᯢ=>~3RȔ}HqTFbE)c4NQMaRwZDY({1pG%lzi#pĕ鈓IV,
C2TM+ri6l<yEIaeD nEUfX+d1Wz#Wk{XL=]\~>'xlh+J<[pIOF 3{|) ڻ;\Ifc#ph$U&/(bPncVT}S`Nr;иTG.%W{㱛^i.4txnhݘ
Y{̌-2" ɨ$_0B5eI)#ƗAX;+ E=>T$4'dy V ?e%	ak	Dk9,̵?Jhs$dÚ'J9_KrOG#x,'J4`eKpfz~?,1I~ VA"a!y$,A,^Ğm5ٝ
Jv0`Aǔ#I>e/a؇D%x؇? 	{H\Ynu-1^AT~ _Aɒ~5ph=_cDbqC<]ypޝ1#Z1ePdlyA\Gfxhej\~13pQs<CJ9kɥ" 2"}j]k}q.#1D9f"C[&1wymJv(MP9Y $9[	+jNn
lV$R7-mO$w
PUdF΂nfCc?MF } %MQ=l-.QVfg!U@&,<':)+t: 
 ,=vRUN~T/3yHՒ(ϜD*܊{j@?ULXlAS;dwh
DAtuՒl+|SS/x?jE_ ^c?+[HxE:RT]Cвlj"L}ոRu m $mW0oʶ\愃7tXM,LVs-r.x)).xمWRJ_H؟F.\0iϙa>)f`՝R3@R@MFt:8hsl-tD*p<h}[*!X
/'&#j7eBn&CNHb쐡)i-Ryih^6MM8(h`0f¼ihaͭ3NX ?VńY\6^w>"TVe,P5p+gʖ!VFo:R	U
[ 
`5xc͞Cm4D2?t}n5Y@IDkEV2RY6|Dp\	HcP7.]y(Ј9lnI-2ϯ׬TB*Ƿi=-U]! );rWB݈DR
I[mXtˉnvrcmi2KX82ks?	hc	v-^1]3èzvhؿIA	# !Gbr1<'.Q>Z-c'*'I
6<;3L)B7(jq!E<ҝ(DL yЄn {47BJZ%3rtПUh5}S`4	1;DTWw>^Ks/<\+-L@O˜lͰnH]aeno #Tm
/[4{[G3uF4	x{0LşMÜ 'ذeTL`:	!-H;{Oa(S&*efoC	ܸq=RBvT4ӵe3n@E&#ddKx47`G5gɨX(2-aADfQ)^mg(4Kk|ʚp<#?6KިV h&p8_RI5F
b̠\VE)2(M"jFփʮ-:
n1@ <)\gB|H-׆Oxx?cu)mV~%y"BC~/X
+B1nmZgQ\UHvW:^CC0-:)"0ZR㘍7Qi)P[L4؎$K ]>c*)(g7owu-IQbdBXC+DDL!i@ 
?:i°+~зϖyY\iO.ޝd~!`^s.NAtajBw*bL4E^V'ea O7
bOϢE2w,׎Qj& $ncWՊҬz`7φCeLlh1Q K!XZ.͐;OjuY6 !XE}_2!d!0fmj.q=	J0V#{`?붶1k^e}=M({[l<HGxpmi}/I|=abAT۠,CFM)BxU`cP!K  Ibնư`}!Z%cj8VlcÕf$j
G4ZwĄYL h<YNYt@vCHNA5Ȗ Аw14V#>urvJ䈮;0QޝdSleNVh3OPOR.#CಾZe	PrR^M^nԑJ`BN`pI&LEþI#E
O8.w+X\nKبH~(*n^1~5}ǭήDdGb\cmQ }eKfd
U
BH: Xƺ-xC^wǚ*gN/ΦD+`QE<ˈ:]ִjI}{_ϴj(V+{z]hΑi) j{5Hh1ucϝ K'z	i3	 R=Vni7cotfpMxUE);	4 E̷[0
8J)^4Fa
~AGLanڔ&1-tpAydoٹ¡R:q'*/j+g(F&$-l"4XXpdʼjʧ%ZטI%e`˰4;iqOT,KGjRõ+Ɠޗ
I
z5Eý{ @H3~w(j\LROTP3,i
()|[08$islPRJ]6MxpHc/c%٬Uy;{Jl{Z
ZR31=EJ"=Z{٣T?q'{_gz
`\˜c~2K{̎4אc;O>F=bzCʇ02~bl{b{,(1dpG'͋ )˴qlĕ0;'$JS*	MD 29lJ4Ҡ᭔Tq>&Ո6eBb8RBjO*	*eKPL@w	*$UV!Y%Al~ǉd84',4IQ-Swu>:gZ,~UE *^Sā}jeYJ&YlWeeӮJ4tx+T	t
DsUcX*mlhjYy3mxN&6:&-?XY&_H#_CifNеdLA8}/2
1]pcNڗ7UHQ-ԸlSMOrʄ˧*<C:a>53왿@
9Fe3$8Y`C?/Xc]#Z$!Ih}.[lPxq+@YXhulCae=}D;RArޥ-Ng0k`3Zr>Sz#?,DʨkJ2PbwkS'dLVzlڭ&?e
/'APk="#\Bpۣ%L$.*¼nJ)ɮ'ufD3>غ@'@h *SE2b
jzd7A3&05/ 	jUV	YRVh
ZI-Q>?\7ݱ~(CNVC|L. Hgu'pS;Љ|Bgx0?`pƀ V1 ڃr}ѧ uvjۮ
", a+"/4>WY+dn	wjEf娶<ӄ^%VmcYm+],'?=MYO$NQ
Tlute}
La}1<Ȱ'8&	.6.`p]Cw
mÑf7Ͽvl<ywڱh"<o>~k7wjӁk l8&
HaT=ʾ8c'0L͘]e
0ݤ~~tؓOXٖ(!LdWslNČ(cـV(Q'ɇ]!IÒd4*n1
%n 7qFJ=(/8hrgA+dæLpLB֥<R$XOFԤ hflYL/ևw!
	&M	2	*uK&+ .&횥JzE	,ӝz8{0p!ma\0?$USR4lФ9U6<Phc)kilIe+/QN/E/e+zRiq玒JŮϞ$ʹAR9ŧgCpCoEc#Qr6&2(+qL	YceSch9
C&f.}66u`GC^K4)et%bO%{ṚQ'<,1FeFHĵQ(\ ۨH2,:՜Q.!wMB;þBPJS4Yw/8+|IUhwqɬ{t%iVPܓ|\G gC:+yiUB&*J^;R'꺚Ԑ5!wzE2qQXUF{{	 *m4OJl%<;; sN,î%ěE
L,WnI$F#qIhi_iOpA-<:pA^	-Zy:1Oۥrxcǈcˤ֘TS>ny4ENeJR'bI
n\Ã
(Tr{i%({5qXql*eK0,Չu%ƷPzjL 
lث8Dwz\UhkL#>S
J!+3dd_(Z;laq`L#Xs_qovy'[DN>삍r41*==0h_
]d@V_,6u+RbXON~A}r$F_i,
<fH@ĀkZ38	<sz4!`&-U>IX)qդ,XҶ~s4?_|iIݸm*ɮ֥TJض54/	 "zI]tEBIgVS Be%3P[tN1nA_[/FNٳ@֋U -ߗ%j5V*u`IIɲ'rz~OJ%/&JՆb))iooq_TsfBJZ*}Ww>&03fhPR*<·
C0GX*(Eڻtn{
p'mQg<P7'Cȏ
}S5\l<iZY	};۹ͦME~Eߵ¨a|-5{hh!$^;{-A!2	pGTZVzszъXW'Dd<0cq=Rν_g/g9a!AZNZKU*w8%?~a?'U%If1Tiߴ3|iZ{aH;q
y	X؝76?POy),\A+ہGI\[b*Ьq]C2$;t([f^I#e">̰E*j߭#.ILJ}IZ^ݬX*Fn-E2NuwZ4F՘X#.WF
|7K^1!Dk5GL>G=sob̃A^odA,(Qx/EkiZ:ɚ;Y
pgOP%c]a3@XR)=u
xp?%Al"=׌#0s<T-cERMm
Ɏʥ 7K~e2j1]SjU1="	BƧ+jbfY[tFӑL2xa#鐺|N9hT;?Yy:nh!uy[}.b^K*cό6Oj7K<fp]	7Ay@O+&"^x?+yҚWTfx\D;?X1iTR?f\~$e&)R8':kѲt!x`7LfE6=7iXxtEDR#CXraǄʳ,⅃pƭUYI9{JwPrJt9M'TiG'(CX1rNѩBitq;|GD!ޣ5LeV(wI޶p2EfIxaz'*:!&um\(hA+غA
5Rk6pWR4'x4vW췈ƋPK*gV+U-q_#_PIڨ16bAK$9#=jA?R߄=vJ!MAsY3]{,LBIT9%b)/?x:4i'
 Wc0q|+LyEU5jiЌ{?KL"q/rWitgGW	Ƽ.iuoa@M\Ld66J
f,Fpg`F48fq]Q["fmn+l?L+p5gv-.ňQCVs/htZ U[sbmhdrAdc'zp	:Ձᰧ`߾xc=5)lUDP
ox{iC]m
J٪p1UtwT;0("T&A
)7+:wS2I<9t5,QGv,#C͞uE
.aN>&0ƑlB2@a^036k`$\fQg8HoOc}oKGQDEȌQ)s:/!-0ˠQ&/==	{VՄyH9@آх+cb}HB B{k#=,7`>A廉߱fB./p?@fa]v7BuG)'*o 2nd@JW
^ǅZ):h>MvVݘ"]RxQvtҤ::SĝҳK	Jd}Z'dHf:Q*
8>ҞZQ
EKP"XE¶0 ]m)rDmQI$
v"k||Gɦ*~'1E]zH;mah}O =.{m҈+H@+T	FvFI.Ulʧ>gH!E<VTbde&(aǪE5WdB.n&VrZDyLO+l(4uӍw5фXk	M#ft`3Տԛ
:eSkW^¼лD
#A1î.Itzu,=ϼhJu4s$A\eK5,~+<ll*
+0̦9StnNOKf
^Gk0{ѝ㘩}Xz<nι:yb;_FEKkrxq+)БiswVEohsiY,2
l8.q>tPwpzM]MTkLE
8$ʫ	v3\qԲKoexaoxFĢtsgm1ZX'ɊKV\c6":j4Oϰ㷹G%cydpfCkUDi@_0(xy$YEKwq
7e4&9hE[\oI&Ϸi<E{u_a.<<7},` ƂRDY	DnL]!C'Qew

:[ch{~iGJg;7;S1qinL+C<+$dk%[%Rߴ!@<^R{n7I^`B C5{pA0LTꇸ7o#?<9_a&)!K3$7,t?<Y^fj˞1Ru)CVƄGw}1-ٸ|j@ 3J;RJ^B<7,[xg9X~Nޕ<pN{5|=㮏8vrK?Sg^iRy\ϦֵCg} @?/܇
.1Y<azq%/uԍkB%2Rpfe5L¤EqvJ\I-QvX5r8!XMNh-V^|ʩ ^W,6$`α!JҕNLO#J{#m2S[!/2vPYajt8ؓfCҦ4V ༯"]b:7iV=izP,K7@&]I|6eS_	*#e8e(}#P/yu+`'at	ątSt@?j
OnU3J?Yh5t2zPm e<x
3!x.ГQcIn{iGKZ5DN0hEA@sH3\y3ñ|"qXdwwpED!bp On}qzs	wO9Gb^IOz;D%)F^DJ߃=A\p|t2쭬B7+[^Bsx:XP];-|gӧ@O ;5܏3+Nww3ܥ]efȋ?pULE34%<1)i\N1dB"k	z2=
JvXU%.Rұw%M.h;iU=Thm᪜nxმsr/&>nĠFQ$sqr	ye	\b!;Z<٥%uG-x~'i]4!zXJ7KItSG{U69
t q&DlebBX" rtGj̍M5ZYBF;ˢ!W
(U'lyԻ9URI
q|z
T}dr!%~jWuQdBY#dlԜc;Bv?<T5'9y%cYo.uqW[	ǓZiԴ	Ն"!8,RRrv}ӹvHl:[F=BO]ǺUtudIS:szvQށrR٦CۍF<eeHi N]*θiE<F%8Aw쐫hY*A<st1dL&_.CT5ng"+]MmS_=cyax(niE1}NuK%\͆җ@~r5FS.vӐ`2FsBvZ?B6YO1:<"E>ۀs§
-'bq̸v\T85q1ĝs*Ca4eh,ENa,8Bg,kt^m7MTx$)K5V9$OYqlB\(89`[=tHpu
UZU=`[שz</lבyg4]sr~6Nɸ<zH	u6J(UvͲD@eUBڳu~鯣	E/!d5V/]A#*L"źx$T!ΰuRUgPuq:3LZU04ayDt`В.pY`yU%<:i~p
3^C\Tؠ@;wi;Iֽ}do{d8KYpSt
}I5)'R%BAEg	Rq	$5!Auuk8`kGkWl4L'~sApA&[0vҐry6cA»eG5փwPzDm5@8o HL 8\W-[E U}_VR/(_{}1/pT.uNdXhHQ<409PSd"WT	:t
X+MT5K[2L<<.n*jzƄ%牰ENw]f,8
/`.=jjUaEBxg/lmX*PDxzz[c/A
ŭZw3lbl7{V`Ǡ{pUF"f=%ZGR_Cmn1.1 9彘2xaV5R
6`aԠ@W*F_yՃ`a@Wg_DjX=<&%d85I([)ZGnʭvAd°0u=ԃ6a0zc!dJEg\Ǭ.PmA:"+%uգ)J+!H*CKW
9UYr.CmR֌|BZjX
"r<,RpEXOHMq	`8ؗC`k&D$,8;ǾڽFKxh!XR9;
!!7@wX#7.7+wnr, Xg(uS,ʌ	>I>#n&ҹU&b\E% Vװw`zrNz.D.ъK7UQG Ls.F_놙w蒸]ig
U}ZhY2IVgc7@eF +Xꤽ0`^Ll403m)XCǴnD{97r6L
l͎'r1--ќLٍx~ݟv{q#9HFsHS)h^Ptg~5?<8u3 NwEFkL$иY=Æ7
$5THJ4RJq5h lF	2v0(W{h18,\=8	.ĭfsA
^	B)LaQn40^y#	wJ"1EVٗpX$9I$H3Wu^Mq* \ ozzIFf
349F
gvN7G]6IuNPhrN%I+
RZsczmܜv8ɜ#ADwA_ـ0c+)o[4KX,.9f,ԁ^aw]h3n⻜GH;%4%G9+%6}dHxA{!IN^/\gT<k$T[d#&#6ϼC<Br*m16AulMG`>N	5$PY&z9\=CR. f?<
JrM(͒LXK|jcD 1X^sR%y,T25zZBJ$a3h93Ɂ6%ĉհLLbSP
K	V_B	&yLjL'2-XV`sm!ِ_KNyT} c-co~HyD7ִ:DY#N	<uMyZnpqE	ݘlpf7>O	Mt7xY L)jЋ4"b
X"*e Pe
+V83LkaLfϴ>ZrSO˸.7o|1(!\r_g$Dߘshm60W	dQ-zGv./"$ɄOQjhӽvWӽ{8>Fi4C[mxʨY5JD쯦\[!1K;MB,fYhZ7C?2u$5hR΄NN1kcӬfq{eA}
/޼y#75yAfo39#~wR%.*~5/{0]CU]_)wYFu&~o/<+eźĚ'$`͸Z.Q|<#V|eϕ*a`*jX$y4pe.q#bDyrpݥ'9USˠs׋f[[/|<ogf7]ﳛ]\݈*అatKl?WYrDJ.dĄ>_!=͐']aoÍƍL'o˃oN:2;?|upې53{&O	+dA{d6*'q2zSj($ϲ
UZ|q1!Q?cCޏc/37ܿQq?#|yѩ#ҒQpk.͗P^nVy.~˺cWU #/Yd9uXӲ3p&~	`_3tQVч<]8)uxHh"ajs{6iւ(7݂I*9<`|SLY6TzZ1@b>cv/./0.#)ˣ2y9<}08+`#`=ؠ+"Q
V IGW#jV)~{]&kD^/
+NޮidnVQ#9`)¤:g"b%5%ͩ=DlcNt3lf~3t8phʹ.e
՗x	ioh2$@e0B=2J+{o7O
WruB !XJz/
Z
_R멪*͔#Fdݦ'@:nβZl,Pz
d$V0F#Z:0 2AJ{


[[FILE_START: .git/objects/fb/34abcdb84db988a9ec0e41e4be4c66a7171f44]]
File: .git/objects/fb/34abcdb84db988a9ec0e41e4be4c66a7171f44
Language: Unknown
Size: 17,513 bytes | Tokens: 8,742
----------------------------------------
x}r9SA-і==Ÿ"x%9l"Rx;,Rګ}Owd/H UEv=nD"3 Nǳ?Oֽ墿;/IK>|V:̦l\b6>,rvOz5]ӳ{e> y֟eQ0/ r=6[L2[ym_.gS_.EW>Y|1e	d~MF$[^5(;qޡ3`,}Z+qqk᧾ )q,ҿG;٨Ch:/(:6y>ŅU".;ͷwrãl|pV(й
fa[}w~zr	Lf(8=`,_X3|F@|5<˗aޓ%y3b6gi	6)<8|Iݏo{?${}{/AxDwg=Z2Q1{<ov_{/~Ƕ 198`P{ދwo_eߴϭ|
Gk0{w/N֚z2@%^==P	t8ξo;Oc!1'/ ||RL=3(tCb8<Nz63Rs2HY1ӹ|9RY
Fg>@|>ϗ @ǲ_pw㱼,(1[msO/[Rsc{?,Z#%&'SR/}>ߓ;;WyOh]uJvMg?/鰫3Ծ>.J{tZL4䠵 .A&%B QS}8yg'/{GNNStEY>!EO׆>CU%{?uM?Z̖lF|QFM8C+NTR8;^,oA1ƟE٫1˒jѕ10{=eYJ]/ϡnNImW- M/^B|
 buН*	vfpzn~v[LG3Wut\@>]5ΖeVVcOkt'ϊ`Y9̊Qs,N_zuH?xAg28܏E)SZ^E<r5ﰖ~D̯!T)PbdB,_|^v\GŜ﫼 fЬfkB٢?d٬5M:WEP@Y
vge޹f~ɧr},:?1ew %ooдNNrP#} ]E?
LF\&BR̫%l6Fh%H{Û7޿Qw;}SŴ'B|#grqmܐo3O
OH'fWhȣ1)":9Vrb_@vO케\΋L:)b66^B*4)a>z=e.hG-|og ř"ϼٷ(4ci
W	TgYaMbٱ:ďW6;bɾ
|qBOu-~o(c}<(5"+)TZbzf!2[Gs>M9Xv@SZ	j0A9e6L,F08yp;-)1,ZLF	JbӬu?ƥ4ɶIB OBJʻ;JKƞۗju6pP5$_Xx	cϞpLguhڗٳ!e,O2"^ۈH!5ѧa[t;䝃RUKdhk7{Xp$chn9
ԣMaz1o-
uz]YS\u̯E-.J:gŴGQd{{{
'%YAjWX6FazV-S} [̏-,Luղ\ebИ'TY9<$C,Kv.&y4'}#CiW=(=f*ԑJ7WuVUVR >6 LgYTI:oħIz*;M	Jt, 	bRbSn:[[bHUVLWjJ|6Puڲq!<~6[dec)I>yك
c
>'VG9T'9-DVϕi{#\Vs]|vUnֱ[U:z
WRCi_O8~;j=yr h;r-³&{>^?J'g{sxlpE>I "dw`t[qFuAA{!,quqTwl7 U`q*C5LvbL[2oݣW-a	j$5w	8jKJ˛vCU{Џݏ"CmAtxJ-շ1Ͼ	Ǜ5͇֨C,2h
iͺhvsz
fX+ʋ烮r_l'6qCG=e|]i%g[rM7_J
wv 7_;UK+Sf|xaY_| ;p} ~got}HqՔNƳje)_`(f}Fhc0ى{4Nb,(-eBegGʚ#lX^U9I	V
C2TK+j`5Y6m<j4u{#ˤ0i
"wL3GkZ?kt=,٫~H&r..>*?^ 3ZF"e\Yr/{޺#=:r
mX.v}'J8k&bPinCmh/BZw}j	\艵F\kSG6#WG㱟^i!ttx~hB=F~OJA-Y`ida*k/p!ځ˨C,:Kp
2ʘdk2 + ?e')a+REo9<,lfw#>|WTE*ΗrVkRX&Yŕb6#ĒᩇWUPqFIt-?_!π׳3cRe&EA`:#y>2BI/ZX#v?/X
%;``*XBƑe/؇ZVtRozlYY=L"V?AT~C\A Ɋqd+Z{ؽP\^ox,NFF8o/mx
g_*,)H`1k Ըb`b1ܥh.9)R@i.;JWFŕ$p2C4nt83DЎk./O)Ю Ei1'F GykޢfC"ŁpK8ٞ
Ex*kQ$=dXݒ6X%u[ļo
[y&VuJ\Df@9=B&#e:`_әuǬ,ZD1!K$bJ3?w1.}:qkeÜ^I2a]!APܡA/
+FQ%!-VĚo!n0F% 1 FDo	 iuHQ~{KL-B"BǪBIJM gտ{#<٬n'/Z.D'fv1gZh#J?Cr}D%&ƅ6xG&m9eXO9r4HJɌNhIl8`+mYc$SD:bb2a{ qCY&2B]w]qNFtJMyO)HnmGEIݖ@3MC)Vɨq:&,w^9Tɤ*chK\q?7X]Lj%``Vk>Pٗ8S]TN{Z	~,'Y)@oiQi_)$'zzd0I}ܑ搡m]' Qs4مJ=199̯6lTwB*Ƿbi-U]! );r_R݈D$ȯ!ϵXBPX\I@Ko⌁218F53=ud 1@r$>Ѩsw
)\F6WR 	m8M-SJ0zp'#r'e9ѥ%
 ;ڰ
a`1|ɯ=glA!ZTME^Uս7eJ S>Г*'<[3l'pxidi% c HU~:NxE1E^¨_.i-Lh'a3p2	+6lm"ɦj2XrH|k: 򿈰F̲a{0F!in\8uF)@;Sudn?x>mfQ%ْ=6?d͙f2jr5V*
m0AuYL@eW;Pz#-ҙ\64$.Cl* ƿ&p8/	#	v?fԊK}uo'X`BAPdHg7FLk 
LHLfQ5r!Dc>_V[C(c߈lz7cTu)mno$y"BC~X
o*B5n}CZ5͂(Xot·y$;+r?C0-;"0[}Rqh$=n4Ze
DQlR$>e1Td3k͛}9޴l6}1 
,a%2"Up3C /fe;ywEg+,c-4`'r:հ@t'u/hHرnScCiݠ9F˦"z\,8,t dނ/Cx-_$
y|*z5fNR6&|՜1_(6`f~B.bb
bf4r?A=C)\!<i)Pk RG"ze2C:)$/=NC`]s3\(.(YvIA7كo !YxtoIi%K,`eAY,GR*jƒF@>A1}waCJT1^$#Tf6$j
gtZ|wĄYcL h>YAYtBnKHNA5Ȟ ѐ12W#>uJȑ]M<a?f(A+v
u\$hO8U{Fd (&h"V%˭B:o_B'QG(&p\gⱸ/a>j 9c@0Tݾd9V{]6*b{&@JWF}Þ<@:慐Ư`C81)kʪ`gvz~oUqGS,ct_Ӻ%1q~V?ad[&0BkMO :O~ES7	$?ҠN_c c5y&O'W΢
</t}WZXO)m!h&[p
8Z-^,Fa
~AG\:`NmJbaĘS:8Ǡ%w\npO:s?T^Pi]aW-QMIR#ZDh޲N3-I
g+htBYa62d9Ax$j#u Gp
6$GeGAN"޽0zan X$r;u^.gBGi'hԈ6tzTL^He-~嬽]K{v(i@#nxKmpHs/cK"c^^u	z<UbhX˻ڇ=j'x5 V|(SRi_'6[F@T0nebiK  E$X%Cc,8
0g$l{y6{R>Ca?mcAtQv/Uiw؈+i3OI ?k]=l"aS2~bo{|ԄPwA0E]$HAƝۭ"Yv CXEj$=@q9ٱ7	'"eAL*C3][ΏYlu_4vʾf) (q18ޘ(|ʆ	{&Yh|t4+"*ew݇
kM@oȬFh&jsP:|7`eQm@"6FS,k?4H0UVގ(t)o/n䫚Ң8Zhq6gvo77=ʵ/
:Gh_RT3 VH/yj6ttzfHPYl$`G?/Xcrۍ`-G%Rv>[6(Z<
Dc鼕l ,,:2dw:R㲻OP|[$iR
`t|Dg4;F~
YQ?[X<^nV*eX@í]a2	X&jXMκ5`8V? D~)V8t
B]pC:J
-m2Zg SG8
zPIɡΧufD;>غA'@h *SE2b
&]`! $\:x[$dZ6zMWuZ/NjBَͫEY2w*`zF6;a:݁N/`DS
?$|qk3
ѾF߼zs '?}*	;Yl'vΰ70"
)2xC烽e)BpNH+W$`?oPjKnc99MMbjm;6&˰jzA	%吝ITwE˃0?~y=iXfI4Mq&(448qw
I{jkچ#ͮ۟?={dncF&Y~t"fWpo36F7l&- 6`TNŁB9FO*e_G}yf,MJ*m~rGcGns?$<]'\l]OoT 5GhSx"13X72*IaNHnd-"565[]&YiB1^.K32{zyuJl&Ű)1]g~>1#9/s
ןɈĥܝ-	_Y
!7mrh&dm\bU5훧JFE),ӝPv{a|}70
¦idGLRE=5[H}{P/hs)*kŽ**U
WTFy-ZJj.^}^|Yx\GbO
ʹAR08ŧgCpC
oEc#Qr6&62(qL	EceiWc9S&mu['LWZDXԁU8xa<ڣICiZʟFqS)^ThT
"yr̰QqR%ڨFZ!ۨJ<dAQ=Ytm\Bv}Xi_pWhh/{%Ӣ 5
oZaw3 V>h(*J^;R'溺P4!z͚(,V*QN ܶCE'zf%LDLH8Y'CaWcd{AX	nI$F3qKhi_OpA-":qA^		+Zy61Oۥ1Zsıe^DjLLR+W>ny4ENeJR?ļwݶߕqyQlQv)i;KQP<w0k
nT4F`XݫkaI&M?O_C%j:1! ,b _X?%q.oF[]
 Fbq4w*hzu%晬7)hvXB켏{9%h5s@M(_v{4anߦW5 3X}DGY)v+'J)bW6?89MIˁg0Þ/MgQ4CzvWF8Xksp cfGrZM7
hQCDmz}:R<\K+Yq}v4 [=iM8"u6ӖP	V%US4)ӂ+}*P$?!ęt
paMI# 0pGY*qj4C1ZCB7RfOA.NWaypB"K|[[GIh%5'+u(>4PV|OAvx
	qj}Qi	)9۸;1PcCjRo9V8_Z'8[VـFG)ޥ<v}$D-dhVW|kN'99q٠f{7I1Cyz@"AFw0jpE(H>cV:ل4yOxtqoPq߽DvՐSE	pGLYdfszъXW'dd<0cq=RF^spBr͐ j 8R,v>0z/T|Q$@7*&/=Vt7A+HZiQmpFgUzdpK`DM:n[XYUfJbŖٲDTAdI13ff
7:v-KXCIT{kվa^ȭH8CƉ0AMȖ@n5fֈ+䢸<?Y1b}vcH_уFr~׋1u&(rۚQ|1g8כ'%e)'JL&^>nK}v-]_'YEO6B\!7b| lFK*=fǮAy'$<Mc~ 74kzP-"ZjHv4.Y]wֈRKw׭|Ix+d|ЦR>m&aV@5LgRQO=7Ȁ4uZA:Muɢn-mEiȫn4p]+Hcf|yNcxb MI7y@WkXIԏmvWJ58я(-tz+
+&J~Th_$}D"s8-+J^~2]mc:~nO5< ZiÓH*j`"خ;6e5)AIb4
DϿ!BV.FfjbHSޕ21RF/:wajBKv%d-3Krۆk7[
<Qa4YTIKYU[W2ءTj7]Jvk05-!b }Jw]=sI)TZ6}LX򃱠gВI0w$G-G
#p'N锠#3O<ڛ;GR$4LYc##YH `@yh rI3ǷR!i̤4E_èvV͸MY.Unku=n `<Xܘ2$-Ϊl:!w:eEf3kbnbzfDcG"pJ5UQ8,b6V:*]>ɴ\~JfN\uhf='8>N5oR$w+zq޻ˌ";փ[Lmv=
 ;iJXeC/"fodqmD <8OiX=<xC)[5.")jeC`z'6J/$(="uNUzJau'7#_!E|d(6A<%,4$8*>A
w:_0	WaGoF9 -\RYQ?3GFI,9]+0ˠQ&?0z<=zr&!u! aEKdK"
9lb4\aL]8PvKǒߠKt 
j<J9a]}oNw##Uq8R?.J@wqr{l8)r>4)%859)`An)M3E܅}%=zyY1y*ޙߧH;R@6lSݙjxYҀ#i0$	57X$l7NAjK##|coJ
'`}Y;*>u;)ޞ)
0FiC";ǈ2_B\&JnL_{)=7eJ5Æ?]nG˧>gJ)E<VTbde&aǺE-WdB!n&VrFd~LO+|(tu[!j	xpޅG 
etbsՏۭ-6̇[UW7^G[o%6@
#A1Ǯ.I`\S8uU,ç;ȼXJuts,I\eO5<~komWj+0g9Stv>~qkx	Eqcn'#~9綁.6`2,r-_\QӋ;\1MɇL;7rC.U~M(LjRa{AvvIQc3B@lAԤk/9̑?Ӄ$Sy*r[^,򼘛XQnLMX^@-Fkq$E11X3m.E(iea=(P,
^^ IVݻɛe
h5i:!-\^$4vp`wuσ@U>x0[gA ~F҄"pe7&ϛޓ[2r;
:ھ㊇m#miG*o1<p܍ixgubV$`D6dٞpG<K*s;")mhc]-"P
Uk>MG9Od(4OVq*pkIj(RL"M*oO0OWe){;!)fg1!]_Lt>[2(L+VN㮻ԸV_dMr6cYIB
VʻVΩx?joO룃9RԙQu^gΕC} @?/܋.?2~uz2ZYj/W=_jV{[^{$|P,OqWY+k`|\*:qxk],&'u6ɖN]
+/>T o+zaVlv³α)J?J'N分^jy_&`<ĽEJ9+L<{2lHJcH ·95ew"׹
].Mӓ`E v8 =R$[ŨѓLe^*3U8U(j}3P/E,2LGVa/	oąl83؀~ 
۪a;݃1Ĳ^uXz
t[q+\ГQcIj{iG˳nˋk94)`7/ŏ_.$"1p},}WPau	,ނv^Hя~-|qzw	ַO9Gb^'G"U#nώ^EJ߁B\Jp|llZ6fv
{H#ꨅ;WP\uE8i*qN5!v1IoMf鮋lt`[
d(JTf)E<-z͕slW]u-!qWOҮ6o,\U[Jz[ED&	^NƝێ|}Thk᪜nxმsr&!n1؉C~9#Lh2<shg,i+=hDHBG{"z;\@+U#RtZZŸC?s_mQ&AtN6[-+!%;./.GxɮVlT75YMmn^auȉrJR
KV'd}'{W+)So"K%!clWd1ΰ桪!u^`(3`ϲ+qF8KMPOί6<-w$7aR׳.TKG
cýdl72z*<}c;O'K:oA'SK{KƶBn0)C̎ȗ-<Gjqں=o wM1z6BY.Xf9T8AK|N¿W9ZUFUlnU24!:hNU9ԏu<UY÷&nیmm3ƸYXAB{VTZgɛJ-X;*<2o
 "#V1>wWCNCwK
Ymbp
!A&|A
bژdqx>b rBeD2}&PwZ[Nyvq9*CQm24E#0BFg+5[;]5	DJےC9|5#S`6 e3. 
A?p_ǧ(\7J^Տ6Xd
?!xGc Ou$AM\W&CjlrQ
?@17t7h G *embKM`(Zp7\Vkll!_*81[p$g(-ŋ%$٤
qͤl[&#(6m#2sŽW 7)N*s,&k9WmUFJ:#du_͖ss,2"BܙVgJQѩA(	vV`v2l{#qpS
cI3)'R%yRAeoRq	ԇ&-Π9u0u+V:8CztZ9׌YDoaz1QkG@`	 C8Q_~dvN?ik}=$T&Xtߪĭ" *~VR/j(_{s1/pT.?MVdXiLQ<40PSd"W	6tXM45+[2YL<<.nZzƄ=ԟ'B7-(*me5Ýd9ǉ6&jdu-uQ=f_8@	1no1u5Tfq:zϰ=d'qݳ.&nsdoi{[:7rF1+y/Y2d?F~goty	U3<wH\-m¬A
5|'̾`R`@_Djxl<%%d824Iz)ZGoʭvAdqi|s=gS%46c0zg!dJE\Ǭ.Pm
!VA:"+sգ٩TBJ+!H*C+W
hQ`WȡxVfLD:f^5Yz	9rA)"@B&<ʄW0K!1u"`IGyFiHx1bJiyp1ᱯv/Rp$C! yHzMgg!$^ wص5Etanmy]3p@50_@tUY02	ۇ=y}{T3ҿbDVk^nuXv
kLOIüeyTT-ImZu1Hi6hk4]W?"̽5K&:"WpF`3[tg-Of>[,q?01[^ JٱVRmFwF[u7?fVrFґ?nPS)h^ys_g~Ym`:H SF^eFkL$мY=ņn$5UHJcj?@fqk*NCPی`
2Ԋv06{h98,
bq;9 }T!W4M,7J
H/={"|⦓}q*ܣIINI[#ǌ&U]WShaD([`ܡpɌ;u >VFOot::ex׶YNzp-"pF{cwB(	NR6H=8kÍys^ڵ$slP#&VRaV*o[%dYxY30n}@;څ-x>Np{q! 
hc+J|~QH'?`/\sa5u-e	mq506}ْGxnu*|sMymlz-7uwvXO.mBpM)	z
+C3$@h/`+7(܄" I۬P*3B	Om"{$82bwkAӃ~JֺfO+BXYH$z+="9Ц8,nҨ@5=*W
vXJQ~JcbĪ8J.cYIn̵g9
t#3E9-L"^']N Xע6cB)
ԴF9@4%
9<uM
0=-Lprn(Sᱚ'w; $qHuŽUoW6>d QS$)(kXqZPڠ<2#vZT88CoblٍYC
$
4HȚ01/s/&l`z`ɢB _DH	"%F=gxP?A4C{'퐶xʨY5JD쯦\a{!1'7T3+;uA.vIzC?2$3hR΅NN>bYOw.>+Խ˲]Mzk_~Gn"k.Qggo39#.~ǃR=0\UD^ٛ>`w
!WUts=gfGNN޿2{㮹:f=o-jI,LXhD}9F?<؜֌[1OcjZf>W
<mhHÕLǵcU!TYO#vNɣ.Y^-i]cGlX
'x$J;ZpfYe{~K[Q8,`)
6!ۏ|{D骕yHA(|Fuj顮P o<|#߅8nٸV=}yp듞L/88	Ee?ݒGM
^\6)`fO',^TK\p
`@2K˜KvO-`,iC|V
mhQMfK6uCXd+[I,[5
YޞXp|7NO3z$}Q̏w<h8%W@)Uˇ`|lcU-ojIIK <H$8FPci)`qW4.r9ɊQ>6feĠ ̆h2*::򤹰F$|׫lqVMs~$PIvZ9x}ř6^ *f
t({u԰Lt'15t*\0;X5[Y8'{t(y'o Ǚh%_.;;"$nuVT\b)65KK&hKDDˡG=A}H"IT
qJj?+mitOR@/K8נY:ipZ^CjdoĤt!kc;\pZ
Mlpp0Rx7EtME/F`$U::]mDG݅}u~$H8!XT_T
TD
lJ_P!B}&jg	l/\9vqu'll34izG|5S%߱"{R[P83͇CMNjzWJlvDWS xn{M^xZ9BT&kMO^OvDDRM
;/


[[FILE_START: app/static/js/script.js]]
File: app/static/js/script.js
Language: javascript
Size: 18,327 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/dump.py]]
File: repo2file/dump.py
Language: python
Size: 5,399 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: app/api.py]]
File: app/api.py
Language: python
Size: 13,019 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/dump_ultra_fixed.py]]
File: repo2file/dump_ultra_fixed.py
Language: python
Size: 4,913 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: repo2file/dump_ultra_main.py]]
File: repo2file/dump_ultra_main.py
Language: python
Size: 4,913 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: test_ai_symbiosis.py]]
File: test_ai_symbiosis.py
Language: python
Size: 5,845 bytes | Tokens: 50
----------------------------------------
[Error reading file: TodoItem.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: repo2file/dump_ultra_new.py]]
File: repo2file/dump_ultra_new.py
Language: python
Size: 121 bytes | Tokens: 30
----------------------------------------
# Get all the content before the main function
# Insert the fixed main function
# Add the if __name__ == '__main__': part


[[FILE_START: test_profile.py]]
File: test_profile.py
Language: python
Size: 633 bytes | Tokens: 156
----------------------------------------
#!/usr/bin/env python
import sys
sys.path.append('.')

# Test loading the profile
try:
    from app.profiles import DEFAULT_PROFILES
    gemini_profile = DEFAULT_PROFILES['gemini']
    print(f"Gemini profile loaded successfully:")
    print(f"  Model: {gemini_profile.model}")
    print(f"  Token budget: {gemini_profile.token_budget}")
    print(f"  Truncation strategy: {getattr(gemini_profile, 'truncation_strategy', 'default')}")
    print(f"  Generate manifest: {getattr(gemini_profile, 'generate_manifest', False)}")
except Exception as e:
    print(f"Error loading profile: {e}")
    import traceback
    traceback.print_exc()


[[FILE_START: repo2file/test_ultra.py]]
File: repo2file/test_ultra.py
Language: python
Size: 1,792 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: test_gemini_profile.py]]
File: test_gemini_profile.py
Language: python
Size: 1,909 bytes | Tokens: 461
----------------------------------------
#!/usr/bin/env python3
"""Test script to verify Gemini profile works correctly"""

import subprocess
import sys
import os
import tempfile
import shutil

# Create a test repository
test_dir = tempfile.mkdtemp()
output_file = os.path.join(test_dir, "output.txt")

# Create some test files
os.makedirs(os.path.join(test_dir, "src"))
with open(os.path.join(test_dir, "README.md"), "w") as f:
    f.write("# Test Project\nThis is a test project for Gemini 1.5 Pro.")

with open(os.path.join(test_dir, "src", "main.py"), "w") as f:
    f.write("""
def main():
    '''Main function for testing'''
    print("Hello, Gemini 1.5 Pro!")
    
def helper_function():
    '''A helper function'''
    return "This is a helper"

if __name__ == "__main__":
    main()
""")

print(f"Created test repository at: {test_dir}")

# Test with Gemini profile
cmd = [
    sys.executable,
    "repo2file/dump_ultra.py",
    test_dir,
    output_file,
    "--profile", "gemini",
    "--budget", "1000000"
]

print(f"Running command: {' '.join(cmd)}")

try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("\n--- STDOUT ---")
    print(result.stdout)
    
    if result.stderr:
        print("\n--- STDERR ---")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
    if result.returncode == 0:
        print("\nSUCCESS! Gemini profile works correctly.")
        
        # Check the output file
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                content = f.read()
                print(f"\nOutput file size: {len(content)} characters")
                print("\nFirst 500 characters of output:")
                print(content[:500])
    else:
        print("\nFAILED! Error running with Gemini profile.")
        
finally:
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory: {test_dir}")


[[FILE_START: test_action_blocks.py]]
File: test_action_blocks.py
Language: python
Size: 2,579 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: test_iteration.py]]
File: test_iteration.py
Language: python
Size: 2,599 bytes | Tokens: 50
----------------------------------------
[Error reading file: 'CodeEntity' object has no attribute 'qualified_name']


[[FILE_START: test_branch_selection.py]]
File: test_branch_selection.py
Language: python
Size: 3,324 bytes | Tokens: 50
----------------------------------------
[Error reading file: TodoItem.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: test_vibe_features.py]]
File: test_vibe_features.py
Language: python
Size: 4,145 bytes | Tokens: 50
----------------------------------------
[Error reading file: TodoItem.__init__() missing 1 required positional argument: 'block_type']


[[FILE_START: fix_dump_ultra.py]]
File: fix_dump_ultra.py
Language: python
Size: 5,957 bytes | Tokens: 1,302
----------------------------------------
#!/usr/bin/env python3
"""Script to fix indentation in dump_ultra.py"""

import re

# Read the file
with open('repo2file/dump_ultra.py', 'r') as f:
    content = f.read()

# Find the main function and fix it
fixed_main = '''def main():
    """Main entry point"""
    try:
        print(f"Arguments: {sys.argv}")
        if len(sys.argv) < 3:
            print("Usage: python dump_ultra.py <repo_path> <output_file> [profile_file] [options]")
            print("\\nOptions:")
            print("  --model MODEL      LLM model to optimize for (default: gpt-4)")
            print("  --budget TOKENS    Token budget (default: 500000)")
            print("  --profile NAME     Use named profile")
            print("  --exclude PATTERN  Add exclusion pattern")
            print("  --boost PATTERN    Boost priority for files matching pattern")
            print("  --manifest         Generate hierarchical manifest")
            print("  --truncation MODE  Truncation strategy (semantic, basic, middle_summarize, business_logic)")
            print("\\nExamples:")
            print("  python dump_ultra.py ./myrepo output.txt")
            print("  python dump_ultra.py ./myrepo output.txt --model claude-3 --budget 200000")
            print("  python dump_ultra.py ./myrepo output.txt --exclude '*.log' --boost '*.py:0.5'")
            sys.exit(1)
        
        repo_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2])
        
        # Parse arguments
        profile = ProcessingProfile(
            name="default",
            token_budget=DEFAULT_TOKEN_BUDGET,
            model="gpt-4"
        )
        
        # Process profile first
        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--profile' and i + 1 < len(sys.argv):
                profile_name = sys.argv[i + 1]
                print(f"Loading profile: {profile_name}")
                # Load from app/profiles.py
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from app.profiles import DEFAULT_PROFILES
                if profile_name in DEFAULT_PROFILES:
                    app_profile = DEFAULT_PROFILES[profile_name]
                    # Convert app profile to dump_ultra profile
                    print(f"Profile model: {app_profile.model}")
                    profile = ProcessingProfile(
                        name=app_profile.name,
                        token_budget=app_profile.token_budget,
                        model=app_profile.model,
                        exclude_patterns=app_profile.exclude_patterns,
                        generate_manifest=getattr(app_profile, 'generate_manifest', True),
                        truncation_strategy=getattr(app_profile, 'truncation_strategy', 'semantic')
                    )
                    # Copy priority patterns if they exist
                    if hasattr(app_profile, 'priority_patterns'):
                        for pattern, score in app_profile.priority_patterns.items():
                            profile.priority_boost[pattern] = score
                else:
                    # Try loading as a file path for backwards compatibility
                    profile_path = Path(profile_name)
                    if profile_path.exists():
                        profile = ProcessingProfile.load(profile_path)
                i += 2
            else:
                i += 1
        
        # Then process other arguments (which may override profile settings)
        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--model' and i + 1 < len(sys.argv):
                model_arg = sys.argv[i + 1]
                print(f"Setting model from arg: '{model_arg}'")
                if model_arg:  # Only set if not empty
                    profile.model = model_arg
                i += 2
            elif arg == '--budget' and i + 1 < len(sys.argv):
                profile.token_budget = int(sys.argv[i + 1])
                i += 2
            elif arg == '--exclude' and i + 1 < len(sys.argv):
                profile.exclude_patterns.append(sys.argv[i + 1])
                i += 2
            elif arg == '--boost' and i + 1 < len(sys.argv):
                pattern, boost = sys.argv[i + 1].split(':')
                profile.priority_boost[pattern] = float(boost)
                i += 2
            elif arg == '--profile':
                # Skip - already processed in first pass
                i += 2
            elif arg == '--manifest':
                profile.generate_manifest = True
                i += 1
            elif arg == '--truncation' and i + 1 < len(sys.argv):
                profile.truncation_strategy = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        # Process repository
        processor = UltraRepo2File(profile)
        processor.process_repository(repo_path, output_path)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()'''

# Split the content at the line before the main function
lines = content.split('\n')
main_start = -1
for i, line in enumerate(lines):
    if 'def main():' in line:
        main_start = i
        break

if main_start == -1:
    print("Could not find main function")
    exit(1)

# Find the end of the file (if __name__ part)
end_marker = -1
for i in range(main_start, len(lines)):
    if "if __name__ == '__main__':" in lines[i]:
        end_marker = i
        break

if end_marker == -1:
    print("Could not find if __name__ marker")
    exit(1)

# Reconstruct the file
new_content = '\n'.join(lines[:main_start]) + '\n' + fixed_main

# Save the fixed file
with open('repo2file/dump_ultra.py', 'w') as f:
    f.write(new_content)

print("Fixed dump_ultra.py successfully!")


[[FILE_START: test_gemini_features.py]]
File: test_gemini_features.py
Language: python
Size: 6,132 bytes | Tokens: 1,369
----------------------------------------
#!/usr/bin/env python3
"""Test script to verify all Gemini profile features"""

import subprocess
import sys
import os
import tempfile
import shutil

# Create a more complex test repository
test_dir = tempfile.mkdtemp()
output_file = os.path.join(test_dir, "output.txt")

# Create nested directory structure
os.makedirs(os.path.join(test_dir, "src"))
os.makedirs(os.path.join(test_dir, "src", "components"))
os.makedirs(os.path.join(test_dir, "src", "utils"))
os.makedirs(os.path.join(test_dir, "tests"))

# Create various files to test features
with open(os.path.join(test_dir, "README.md"), "w") as f:
    f.write("""# Test Project for Gemini 1.5 Pro
This tests hierarchical manifest generation and smart truncation.

## Features
- Component-based architecture
- Utility functions
- Full test coverage""")

with open(os.path.join(test_dir, "src", "main.py"), "w") as f:
    f.write("""import components.user_manager
import utils.logger

def main():
    '''Main application entry point'''
    logger = utils.logger.get_logger(__name__)
    user_manager = components.user_manager.UserManager()
    logger.info("Application started")
    return user_manager.start()

def helper_function():
    '''Helper function that demonstrates business logic'''
    # This is critical business logic
    return calculate_revenue() * PROFIT_MARGIN

def calculate_revenue():
    '''Calculate revenue - business critical'''
    return 1000000

PROFIT_MARGIN = 0.15

if __name__ == "__main__":
    main()
""")

with open(os.path.join(test_dir, "src", "components", "__init__.py"), "w") as f:
    f.write("# Components module")

with open(os.path.join(test_dir, "src", "components", "user_manager.py"), "w") as f:
    f.write("""class UserManager:
    '''Manages user operations'''
    
    def __init__(self):
        self.users = {}
    
    def add_user(self, user_id, name):
        '''Add a new user to the system'''
        self.users[user_id] = {"name": name, "active": True}
    
    def get_user(self, user_id):
        '''Retrieve user by ID'''
        return self.users.get(user_id)
    
    def start(self):
        '''Start the user manager service'''
        print("User manager started")
        return True
""")

with open(os.path.join(test_dir, "src", "utils", "__init__.py"), "w") as f:
    f.write("# Utils module")

with open(os.path.join(test_dir, "src", "utils", "logger.py"), "w") as f:
    f.write("""import logging

def get_logger(name):
    '''Get a logger instance'''
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

def format_log_message(level, message):
    '''Format a log message'''
    return f"[{level}] {message}"
""")

with open(os.path.join(test_dir, "tests", "test_main.py"), "w") as f:
    f.write("""import unittest
from src.main import calculate_revenue, PROFIT_MARGIN

class TestMain(unittest.TestCase):
    def test_revenue_calculation(self):
        '''Test revenue calculation'''
        self.assertEqual(calculate_revenue(), 1000000)
    
    def test_profit_margin(self):
        '''Test profit margin constant'''
        self.assertEqual(PROFIT_MARGIN, 0.15)
""")

# Create a large file to test truncation
with open(os.path.join(test_dir, "large_config.json"), "w") as f:
    # Generate a large JSON config
    f.write("{\n")
    for i in range(1000):
        f.write(f'  "setting_{i}": "value_{i}",\n')
    f.write('  "final_setting": "final_value"\n}')

# Add .gitignore
with open(os.path.join(test_dir, ".gitignore"), "w") as f:
    f.write("""__pycache__/
*.pyc
venv/
node_modules/
.DS_Store
""")

print(f"Created complex test repository at: {test_dir}")

# Test with Gemini profile
cmd = [
    sys.executable,
    "repo2file/dump_ultra.py",
    test_dir,
    output_file,
    "--profile", "gemini"
]

print(f"Running command: {' '.join(cmd)}")

try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("\n--- STDOUT ---")
    print(result.stdout)
    
    if result.stderr:
        print("\n--- STDERR ---")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
    if result.returncode == 0:
        print("\nSUCCESS! Gemini profile processed complex project correctly.")
        
        # Check the output file
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                content = f.read()
                print(f"\nOutput file size: {len(content)} characters")
                
                # Check for key features
                print("\nFeature checks:")
                
                if "# Project Manifest" in content:
                    print("✓ Hierarchical manifest generated")
                else:
                    print("✗ Manifest not found")
                
                if "### Navigation Guide" in content:
                    print("✓ Navigation guide included")
                else:
                    print("✗ Navigation guide not found")
                
                if "business logic" in content or "business critical" in content:
                    print("✓ Business logic prioritization detected")
                else:
                    print("✗ Business logic not prioritized")
                
                if "Token Budget: 1,000,000" in content:
                    print("✓ Large token budget applied")
                else:
                    print("✗ Token budget not correctly set")
                
                if "truncated" in content or "..." in content:
                    print("✓ Smart truncation applied")
                else:
                    print("✗ Truncation not detected (might not be needed)")
                
                print("\nFirst 1000 characters of manifest section:")
                manifest_start = content.find("# Project Manifest")
                if manifest_start >= 0:
                    print(content[manifest_start:manifest_start+1000])
    else:
        print("\nFAILED! Error running with Gemini profile.")
        
finally:
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory: {test_dir}")


==================================================
## Processing Summary
Files Processed: 125 / 125
Token Usage: 102,233 / 500,000
Utilization: 20.4%

## File Type Distribution
.py: 26 files
.sample: 13 files
.md: 8 files
.html: 2 files
.txt: 1 files
.json: 1 files
.sh: 1 files
.css: 1 files
.js: 1 files

## Language Distribution
python: 26 files
javascript: 1 files

Generated by UltraRepo2File