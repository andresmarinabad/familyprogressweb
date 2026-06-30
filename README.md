# FamilyProgressWeb

[![Tests](https://github.com/andresmarinabad/familyprogressweb/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/andresmarinabad/familyprogressweb/actions/workflows/ci-tests.yml)

## Overview

**FamilyProgressWeb** is a static HTML page that visually tracks the progress of family members, displaying their birthdays and pregnancy progress bars. The website is dynamically generated from a JSON file containing birth dates and pregnancy statuses.

🔗 **Live Website:** [FamilyProgressWeb](https://family-expansion.web.app/)

## Features

- Displays family members' names, birthdays, and a progress bar showing time until the next birthday.
- Supports pregnancy tracking by showing expected birth dates.
- Automatically updates when new data is added.
- Deploys automatically to Firebase Hosting.
- Allows users to upload new photos by creating a GitHub issue.
- Scheduled daily deployment to keep data updated.

## File Structure

```
FamilyProgressWeb/
│── data.json         # Contains family members' data
│── templates/
│   ├── index.html    # Jinja template for rendering HTML
│── public/
│   ├── css/          # Static CSS files
│   ├── images/       # Uploaded images
│── render.py         # Python script to generate index.html
│── .github/
│   ├── workflows/
│   │   ├── deploy.yml       # GitHub Action to render and deploy
│   │   ├── upload_image.yml # GitHub Action to process new photos
```

## Data Format

The `data.json` file should contain entries in the following format:

```json
[
  {
    "nombre": "John Doe",
    "fecha": "25/09/2017"
  },
  {
    "nombre": "Jane Smith",
    "fecha": "28/08/2018"
  },
  {
    "nombre": "Baby Doe",
    "fecha": "04/07/2025",
    "embarazo": true
  }
]
```

## Setup & Installation

### Prerequisites

- Python 3 installed
- Firebase CLI installed (`npm install -g firebase-tools`)
- A Firebase account and a configured project
- GitHub repository with Actions enabled

### Installation Steps

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/FamilyProgressWeb.git
   cd FamilyProgressWeb
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt  # If required
   ```
3. Authenticate Firebase:
   ```sh
   firebase login
   firebase init hosting
   ```
4. Configure Firebase settings (`firebase.json` and `.firebaserc` files as needed).

## GitHub Actions Workflow

### Rendering & Deployment

- A GitHub Action (`deploy.yml`) runs `render.py` to update `index.html` whenever changes are made to `data.json`.
- The updated site is deployed to Firebase.
- A scheduled daily action at **12:00 UTC** updates the page to reflect any changes.

### Uploading Photos

- Creating an **issue** with the child's name as the title and attaching an image triggers the `upload_image.yml` action.
- The image is added to the repository, committed, and a new deployment is triggered.

## Deployment

After making changes, you can manually deploy the site with:

```sh
firebase deploy
```

Alternatively, push changes to GitHub, and the workflow will handle the deployment automatically.

## Contributing

1. Fork the repository.
2. Create a new branch (`feature-branch`).
3. Commit changes and push.
4. Open a Pull Request for review.

## License

This project is licensed under the MIT License.
