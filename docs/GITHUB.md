# GitHub PAT setup (write tools)

Write tools (`create_page`, `update_page`, `append_to_page`, etc.) commit to your repo via the **GitHub Contents API**. You need a fine-grained Personal Access Token.

## 1. Fork this repo

Create your own copy: `your-username/wiki-brain`

## 2. Create a fine-grained PAT

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. **Generate new token**
3. **Repository access:** Only select repositories → your `wiki-brain` fork
4. **Permissions:** Contents → **Read and write**
5. Copy the token once — you cannot view it again

## 3. Configure environment

**On Render (recommended):** paste only `GITHUB_TOKEN` in Environment. Repo and branch are automatic.

**Local `.env`:**

```env
GITHUB_TOKEN=github_pat_xxxxxxxx
GITHUB_REPO=your-username/wiki-brain
GITHUB_BRANCH=main
```

Never commit `.env`.

## 4. Security rules

| Do | Don't |
|----|-------|
| Store token in `.env` (gitignored) | Put token in `git remote` URL |
| Use fine-grained PAT scoped to one repo | Use classic PAT with `repo` on all repos |
| Rotate if leaked | Commit `.env` or paste token in chat |

## 5. Verify writes

After configuring, ask your AI client to run `create_page` on a test file, then check your GitHub repo for the commit.

## Local-only mode

Leave `GITHUB_TOKEN` unset. Read tools (`search`, `read_page`) still work from local `wiki/`. Write tools return a clear error.
