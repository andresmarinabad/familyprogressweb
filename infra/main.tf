resource "vercel_project" "familyprogress" {
  name      = "familyprogress"
  
  framework = "flask"

  # CONEXIÓN CON GITHUB
  git_repository = {
    type = "github"
    repo = var.github_repo
  }
}

resource "vercel_deployment" "testing" {
  project_id = vercel_project.familyprogress.id
  ref     = "add_flask"
}

resource "vercel_deployment" "production" {
  project_id = vercel_project.familyprogress.id
  ref     = "main"
}
