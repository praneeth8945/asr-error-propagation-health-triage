# GitHub publishing guide

This guide publishes the complete project folder to a new GitHub repository.
It does not deploy the application to the internet; it only stores the source
code and project documents in GitHub.

## 1. Install Git

Open Command Prompt and run:

~~~bat
git --version
~~~

If Windows says that "git" is not recognized, install Git for Windows from
https://git-scm.com/download/win. Accept the option that lets Git run from the
Command Prompt, then close and reopen Command Prompt.

Set your Git identity once on the computer. Use the email address associated
with your GitHub account:

~~~bat
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
~~~

## 2. Create an empty GitHub repository

1. Sign in to GitHub and select the plus icon, then "New repository".
2. Enter a repository name, for example "voice-health-navigator".
3. Choose Public or Private according to your preference.
4. Leave "Add a README file", ".gitignore", and "Choose a license" unchecked.
   This project already contains those files.
5. Select "Create repository".
6. Copy the HTTPS repository address shown by GitHub. It has this form:

~~~text
https://github.com/YOUR-USERNAME/voice-health-navigator.git
~~~

## 3. Open the correct folder

Extract the ZIP file first. In Command Prompt, use "cd /d" to change both the
drive and folder:

~~~bat
cd /d "C:\path\to\voice-symptom-support-assistant"
dir
~~~

The "dir" command should list "app.py", "README.md", "requirements.txt", and
the "src", "data", "docs", and ".github" folders. If it does not, change into
the folder that contains those files before continuing.

## 4. Initialize Git and create the first commit

Run each command in order:

~~~bat
git init
git add .
git status
git commit -m "Initial commit: Voice Health Navigator"
git branch -M main
~~~

What these commands do:

| Command | Meaning |
| --- | --- |
| "git init" | Creates a local Git history in this folder |
| "git add ." | Selects project files for the first commit while obeying ".gitignore" |
| "git status" | Shows which files are selected; check this before committing |
| "git commit" | Saves a named snapshot in local Git history |
| "git branch -M main" | Names the primary branch "main" |

Before committing, make sure that "git status" does not show ".venv", "models",
".env", ".streamlit/secrets.toml", recordings, transcripts, patient data, or
personal tokens.

## 5. Connect GitHub and push

Replace the placeholder URL with the exact HTTPS address copied in step 2:

~~~bat
git remote add origin https://github.com/YOUR-USERNAME/voice-health-navigator.git
git remote -v
git push -u origin main
~~~

The first push may open a browser window for GitHub authentication. Complete
that browser sign-in. If Git asks for a password in the terminal, use a GitHub
personal access token rather than your GitHub account password.

After the push completes, refresh the repository page in GitHub. You should
see README.md rendered on the home page, source files, documentation, and a
green or red Actions status after the automated test workflow runs.

## 6. Push future changes

Each time you change the project:

~~~bat
cd /d "C:\path\to\voice-symptom-support-assistant"
git status
git add .
git commit -m "Describe the change here"
git push
~~~

Use "git status" before every commit. It prevents accidental upload of local
models, private files, audio recordings, or virtual-environment files.

## Common problems

### "git is not recognized"

Git is not installed or the terminal was not reopened after installation.
Install Git for Windows, close Command Prompt, reopen it, and run
"git --version".

### "remote origin already exists"

The folder is already connected to a remote. Check it:

~~~bat
git remote -v
~~~

To replace the remote address with the correct repository address:

~~~bat
git remote set-url origin https://github.com/YOUR-USERNAME/voice-health-navigator.git
git push -u origin main
~~~

### "rejected" or "fetch first" on the first push

This normally means the GitHub repository was created with its own README or
other initial file. The simplest solution for a new project is to delete that
new empty repository on GitHub and recreate it without initializing any files.
Then run the push commands again.

Do not use "git push --force" for this project unless you fully understand
which remote history will be overwritten.

### GitHub authentication fails

Confirm that the remote is correct with "git remote -v", sign in to the same
GitHub account in the browser, and retry "git push". For HTTPS command-line
authentication, GitHub supports browser sign-in and personal access tokens.
Never commit a token, paste it into source code, or add it to README.md.

### Files are missing from GitHub

Run:

~~~bat
git status
git add .
git commit -m "Add missing project files"
git push
~~~

If a file is intentionally ignored by ".gitignore", remove the ignore rule
only after confirming that it is safe and appropriate to publish.
