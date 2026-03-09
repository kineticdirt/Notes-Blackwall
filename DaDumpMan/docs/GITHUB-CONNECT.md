# Connecting this repo to GitHub

How to connect DaDumpMan (or any local repo) to GitHub so you can push and pull reliably. The agent in Cursor **cannot** read or use your token; only **you** configure it on your machine.

---

## Option A: GitHub CLI (recommended)

The CLI stores credentials securely and lets you push without typing a token every time.

### 1. Install

- **macOS:** `brew install gh`
- **Windows:** `winget install GitHub.cli` or [github.com/cli/cli](https://github.com/cli/cli#installation)
- **Linux:** See [github.com/cli/cli#installation](https://github.com/cli/cli#installation)

### 2. Log in (stores token for git)

```bash
gh auth login
```

- Choose **GitHub.com**
- Choose **HTTPS** (or SSH if you prefer keys)
- When asked for auth: **Login with a web browser** (easiest) or **Paste an authentication token**
- If you paste a token: use a **Personal Access Token (classic)** or **Fine-grained** token with scope `repo` (and `workflow` if you use Actions)

### 3. Confirm git uses it

```bash
gh auth status
```

You should see “Logged in to github.com as kineticdirt”. After that, `git push` and `git pull` use this login.

### 4. Push this repo

**Monorepo (Cequence BlackWall):** from the workspace root:

```bash
git remote add origin https://github.com/kineticdirt/Cequence-BlackWall.git
git push -u origin main
```

**Standalone repo (e.g. DaDumpMan):** if you split out a project:

```bash
git remote add origin https://github.com/kineticdirt/DaDumpMan.git
git push -u origin main
```

If the repo was created with an SSH URL, use that with SSH or use the HTTPS URL so `gh` auth is used (Option B below).

---

## Option B: Personal Access Token (PAT) with HTTPS

Use this when you don’t want the CLI and prefer token-only auth.

**Quick setup (paste token once):** From the repo root, run `./DaDumpMan/scripts/setup-github-pat.sh`. When prompted, paste your PAT (input is hidden). It sets origin to `Cequence-BlackWall` by default; then run `git push -u origin main`. For a different repo: `REPO_NAME=DaDumpMan ./DaDumpMan/scripts/setup-github-pat.sh`. Different user: `GITHUB_USER=youruser ./DaDumpMan/scripts/setup-github-pat.sh`.

### 1. Create a token

- **Classic:** GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**. Scope: **repo** (full control).
- **Fine-grained:** **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**. Resource owner: your user. Repository access: only **DaDumpMan** (or “All”). Permissions: **Contents** (Read and write), **Metadata** (Read).

Copy the token once; it won’t be shown again.

### 2. Use the token when git asks for a password

Remote must be HTTPS (not SSH). Use `Cequence-BlackWall` for the monorepo, or the repo name if pushing a standalone project:

```bash
git remote add origin https://github.com/kineticdirt/Cequence-BlackWall.git
git push -u origin main
```

When prompted:

- **Username:** `kineticdirt`
- **Password:** paste the **token** (not your GitHub password)

### 3. If you get 403 when pushing

- **Use HTTPS, not SSH.** The PAT script stores credentials for HTTPS. If your remote is `git@github.com:...`, git uses SSH (your key), not the PAT. Fix: `git remote set-url origin https://github.com/kineticdirt/Cequence-BlackWall.git`
- **Token scope:** Classic token needs **repo**. Fine-grained needs **Contents** (Read and write) + **Metadata** (Read), and **Repository access** must include **DaDumpMan** (or All repositories).
- **New repo:** If you just created DaDumpMan, create a fresh token that includes this repo, run `./scripts/setup-github-pat.sh` again, then push.

### 4. Cache the token (optional)

So you don’t paste it every time:

```bash
git config --global credential.helper store
```

After the next successful push, the token is stored in plain text in `~/.git-credentials`. Use only on a machine you control. Safer alternative: use `credential.helper osxkeychain` (macOS) or `manager` (Windows) if available.

---

## Option C: SSH key (no token)

No token; uses a key pair. Good if you already use SSH for GitHub.

### 1. Generate a key (if you don’t have one)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519_github
```

Use a passphrase. Don’t share the private key.

### 2. Add public key to GitHub

- Copy: `cat ~/.ssh/id_ed25519_github.pub` (or `id_ed25519.pub` if that’s what you use).
- GitHub → **Settings** → **SSH and GPG keys** → **New SSH key** → paste and save.

### 3. Use SSH remote

```bash
git remote add origin git@github.com:kineticdirt/DaDumpMan.git
git push -u origin main
```

If you use a custom key name, configure `~/.ssh/config`:

```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
```

---

## Why the agent can’t push for you

- The agent runs commands in **your** environment but has **no** access to stored secrets (no reading `.env`, credential files, or Cursor’s token slot).
- So when the agent runs `git push`, it uses **whatever auth is already configured** on your machine (e.g. after you run `gh auth login` or set a PAT in the credential helper).
- To “accurately connect and run it”: **you** do the one-time setup (Option A, B, or C); after that, the agent can run `git push` and it will use that auth.

---

## Summary

| Method        | Command / step                    | Best for                    |
|---------------|-----------------------------------|-----------------------------|
| **GitHub CLI**| `gh auth login` then `git push`   | Easiest; secure storage     |
| **PAT (HTTPS)** | Create token → use as password  | No CLI; token-only          |
| **SSH**       | Add key to GitHub; `git@github.com` remote | No token; key-based |

Use **one** of the options above; then from the repo root, `git push -u origin main` will work (and the agent can run the same command once auth is set up).
