resource "vercel_project" "familyprogressweb" {
  name      = "familyprogressweb"
  
  framework = "flask"

  # CONEXIÓN CON GITHUB
  git_repository = {
    type = "github"
    repo = var.github_repo
  }
}

resource "vercel_deployment" "production" {
  project_id = vercel_project.familyprogressweb.id
  ref     = "main"
}
