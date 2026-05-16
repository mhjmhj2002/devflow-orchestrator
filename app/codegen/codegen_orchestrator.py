"""Simple code generation orchestrator (MVP).

This module demonstrates a safe, minimal code generation workflow:
- Determine project path
- Create a branch named `devflow/issue-<n>-generated`
- Write a small marker file under the target service
- Commit and push

This is intentionally minimal; it will not perform arbitrary deletions
and it operates only inside the target service directory.
"""

from pathlib import Path
from typing import Dict, Any
from app.core.logger import logger
from app.project_context.context_registry import get_project_path
from app.git.git_client import GitClient
import hashlib
import re
from app.github.pr_creator import create_pull_request
from app.github.github_commenter import post_github_comment
from app.agents.reviewer_agent import review_pull_request
import os
import subprocess
from app.github.pr_creator import update_pull_request
from app.agents.reviewer_agent import fetch_pr_files


def _slugify(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:40]


def start_codegen_workflow(payload: Dict[str, Any]):
    """Start a minimal code generation workflow.

    payload expected keys: repository, issue_number, comment
    """
    repository = payload.get("repository")
    issue_number = payload.get("issue_number") or "0"
    comment = payload.get("comment") or {}

    logger.info(f"Starting codegen for repo={repository} issue={issue_number}")

    repo_path = get_project_path(repository)
    if not repo_path:
        raise RuntimeError(f"repository not mapped: {repository}")

    # Target only the repository path (sandbox)
    target = Path(repo_path)

    # create an ephemeral branch name
    title_fragment = (comment.get("body") or "generated").splitlines()[0][:50]
    slug = _slugify(title_fragment)
    branch = f"devflow/issue-{issue_number}-{slug or hashlib.md5(str(issue_number).encode()).hexdigest()[:6]}"

    git = GitClient()

    # perform checkout in-place (assumes repo already exists locally)
    # If the resolved path is not a git repo, bail out gracefully
    if not (target / ".git").exists():
        logger.warning(f"Target path is not a git repo: {target}; skipping clone/branch. Creating files locally.")

    # create a generated marker file in a safe location under the target
    gen_file = target / "devflow_ai_generated" / f"issue_{issue_number}_generated.txt"
    gen_file.parent.mkdir(parents=True, exist_ok=True)

    content = (
        f"DevFlow AI generated artifacts\nRepository: {repository}\nIssue: {issue_number}\nComment: {str(comment.get('body'))[:200]}\n"
    )

    gen_file.write_text(content)

    # ==== NEW CODE TO GENERATE CRUD ====
    if repository == "devflow-platform":
        base_pkg = target / "services" / "identity-service" / "src" / "main" / "java" / "com" / "devflow" / "identity"
        if base_pkg.exists():
            logger.info("Generating User CRUD for identity-service")
            
            # User Entity
            user_java = base_pkg / "User.java"
            user_java.write_text(
                "package com.devflow.identity;\n\n"
                "public class User {\n"
                "    private Long id;\n"
                "    private String name;\n"
                "    private String email;\n\n"
                "    public Long getId() { return id; }\n"
                "    public void setId(Long id) { this.id = id; }\n"
                "    public String getName() { return name; }\n"
                "    public void setName(String name) { this.name = name; }\n"
                "    public String getEmail() { return email; }\n"
                "    public void setEmail(String email) { this.email = email; }\n"
                "}\n"
            )
            
            # UserRepository
            repo_java = base_pkg / "UserRepository.java"
            repo_java.write_text(
                "package com.devflow.identity;\n\n"
                "import org.springframework.stereotype.Repository;\n"
                "import java.util.*;\n"
                "import java.util.concurrent.ConcurrentHashMap;\n"
                "import java.util.concurrent.atomic.AtomicLong;\n\n"
                "@Repository\n"
                "public class UserRepository {\n"
                "    private final Map<Long, User> db = new ConcurrentHashMap<>();\n"
                "    private final AtomicLong seq = new AtomicLong(1);\n\n"
                "    public Optional<User> findById(Long id) {\n"
                "        return Optional.ofNullable(db.get(id));\n"
                "    }\n"
                "    public List<User> findAll() {\n"
                "        return new ArrayList<>(db.values());\n"
                "    }\n"
                "    public User save(User user) {\n"
                "        if (user.getId() == null) {\n"
                "            user.setId(seq.getAndIncrement());\n"
                "        }\n"
                "        db.put(user.getId(), user);\n"
                "        return user;\n"
                "    }\n"
                "    public void deleteById(Long id) {\n"
                "        db.remove(id);\n"
                "    }\n"
                "}\n"
            )
            
            # UserService
            service_java = base_pkg / "UserService.java"
            service_java.write_text(
                "package com.devflow.identity;\n\n"
                "import org.springframework.stereotype.Service;\n"
                "import java.util.List;\n\n"
                "@Service\n"
                "public class UserService {\n"
                "    private final UserRepository userRepository;\n\n"
                "    public UserService(UserRepository userRepository) {\n"
                "        this.userRepository = userRepository;\n"
                "    }\n\n"
                "    public List<User> getAllUsers() {\n"
                "        return userRepository.findAll();\n"
                "    }\n\n"
                "    public User getUser(Long id) {\n"
                "        return userRepository.findById(id).orElse(null);\n"
                "    }\n\n"
                "    public User createUser(User user) {\n"
                "        return userRepository.save(user);\n"
                "    }\n\n"
                "    public void deleteUser(Long id) {\n"
                "        userRepository.deleteById(id);\n"
                "    }\n"
                "}\n"
            )
            
            # UserController
            ctrl_java = base_pkg / "UserController.java"
            ctrl_java.write_text(
                "package com.devflow.identity;\n\n"
                "import org.springframework.web.bind.annotation.*;\n"
                "import java.util.List;\n\n"
                "@RestController\n"
                "@RequestMapping(\"/users\")\n"
                "public class UserController {\n"
                "    private final UserService userService;\n\n"
                "    public UserController(UserService userService) {\n"
                "        this.userService = userService;\n"
                "    }\n\n"
                "    @GetMapping\n"
                "    public List<User> getAll() {\n"
                "        return userService.getAllUsers();\n"
                "    }\n\n"
                "    @GetMapping(\"/{id}\")\n"
                "    public User get(@PathVariable Long id) {\n"
                "        return userService.getUser(id);\n"
                "    }\n\n"
                "    @PostMapping\n"
                "    public User create(@RequestBody User user) {\n"
                "        return userService.createUser(user);\n"
                "    }\n\n"
                "    @DeleteMapping(\"/{id}\")\n"
                "    public void delete(@PathVariable Long id) {\n"
                "        userService.deleteUser(id);\n"
                "    }\n"
                "}\n"
            )

    # environment flags
    DRY_RUN = os.getenv("DEVFLOW_DRY_RUN", "false").lower() in ("1", "true", "yes")

    # helper: run maven tests if pom.xml exists
    def run_maven_tests(path: Path) -> bool:
        pom = path / "pom.xml"
        if not pom.exists():
            return True
        if DRY_RUN:
            logger.info("DRY RUN: would run 'mvn test' here")
            return True
        try:
            proc = subprocess.run(["mvn", "-q", "test"], cwd=str(path), capture_output=True, text=True)
            if proc.returncode != 0:
                logger.error(f"Maven tests failed: {proc.stdout}\n{proc.stderr}")
                return False
            logger.info("Maven tests passed")
            return True
        except FileNotFoundError:
            logger.warning("Maven not found on PATH; skipping maven tests")
            return True

    if not run_maven_tests(target):
        raise RuntimeError("Validation failed: maven tests did not pass")

    # attempt to commit and push if .git exists
    pr_result = None
    if (target / ".git").exists():
        if DRY_RUN:
            logger.info(f"DRY RUN: would create branch {branch} and commit changes in {target}")
        else:
            code, out, err = git.checkout_new_branch(str(target), branch)
            if code != 0:
                logger.warning(f"Failed creating branch: {out} {err}")
            else:
                msg = f"chore(devflow): ai generated changes for issue {issue_number}"
                code2, out2, err2 = git.add_commit_push(str(target), msg, branch)
                if code2 != 0:
                    logger.warning(f"Failed add/commit/push: {out2} {err2}")
                else:
                    # attempt to create pull request if push succeeded (and not dry-run)
                    if DRY_RUN:
                        logger.info(f"DRY RUN: would create PR for branch {branch}")
                    else:
                                                    try:
                                                        # compute requested reviewers from CODEOWNERS if present
                                                        def parse_codeowners(path: Path):
                                                            candidates = []
                                                            locations = [path / ".github" / "CODEOWNERS", path / "CODEOWNERS"]
                                                            for loc in locations:
                                                                if loc.exists():
                                                                    for line in loc.read_text().splitlines():
                                                                        line = line.strip()
                                                                        if not line or line.startswith("#"):
                                                                            continue
                                                                        parts = line.split()
                                                                        if len(parts) >= 2:
                                                                            owners = parts[1:]
                                                                            for o in owners:
                                                                                if o.startswith("@"):
                                                                                    candidates.append(o.lstrip("@"))
                                                                                else:
                                                                                    candidates.append(o)
                                                                    break
                                                            # dedupe
                                                            return list(dict.fromkeys(candidates))

                                                        reviewers = parse_codeowners(target)
                                                        if not reviewers:
                                                            # fallback to owner from env
                                                            reviewers = [os.getenv("GITHUB_OWNER")]

                                                        pr = create_pull_request(repository=repository, head=branch, requested_reviewers=reviewers)
                                                        pr_result = pr
                                                        logger.info(f"PR creation result: {pr}")
                                                    except Exception:
                                                        logger.exception("Failed to create PR")

    # if PR was created successfully, post link and run reviewer agent
    if isinstance(pr_result, dict) and pr_result.get("status") == "ok":
        pr_res = pr_result.get("result") or {}
        pr_url = pr_res.get("html_url") or pr_res.get("url")
        if pr_url:
            try:
                resp = post_github_comment(
                    repository=repository,
                    issue_number=issue_number,
                    body=f"DevFlow: created Pull Request for generated changes: {pr_url}"
                )
                # if posting to original issue failed (404), fallback to PR number
                if isinstance(resp, dict) and resp.get("status") == "error" and resp.get("status_code") == 404:
                    pr_num = pr_res.get("number")
                    post_github_comment(
                        repository=repository,
                        issue_number=pr_num,
                        body=f"DevFlow: created Pull Request for generated changes: {pr_url} (original issue {issue_number} not found)"
                    )
            except Exception:
                logger.exception("Failed to post PR link comment")

        # trigger reviewer agent to perform an automated review and post results
        try:
            if pr_res and pr_res.get("number"):
                review = review_pull_request(repository=repository, pr_number=pr_res.get("number"))
                if review:
                    # post review result as comment on PR
                    post_github_comment(
                        repository=repository,
                        issue_number=pr_res.get("number"),
                        body=f"DevFlow automated review:\n\n{review}"
                    )
        except Exception:
            logger.exception("Reviewer agent failed or couldn't post review")

        # Enrich PR body with list of files changed and a checklist
        try:
            files = fetch_pr_files(repository, pr_res.get("number"))
            if files:
                filenames = [f.get("filename") for f in files]
                files_md = "\n".join([f"- `{n}`" for n in filenames])
                checklist = """
### AI Generated Changes

#### Files changed
%s

#### Validation checklist
- [ ] Build passes locally (Maven)
- [ ] Tests pass
- [ ] No obvious security issues
- [ ] Naming and API contracts respected
- [ ] Add/Update unit tests where appropriate

#### Review instructions
Please review the changed files, run the project tests locally and approve the PR when satisfied.
""" % files_md

                update_pull_request(repository, pr_res.get("number"), body=checklist)
        except Exception:
            logger.exception("Failed to enrich PR body")
        except Exception:
            logger.exception("Reviewer agent failed or couldn't post review")

    logger.info(f"Codegen workflow finished for {repository}#{issue_number} branch={branch}")
    return {"repository": repository, "issue_number": issue_number, "branch": branch, "generated": True}

