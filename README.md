## 📖 Table of Contents
- [📖 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [📦 Features](#-features)
- [📂 repository Structure](#-repository-structure)
- [🚀 Getting Started](#-getting-started)
    - [🔧 Installation](#-installation)
    - [🤖 Running BeamEye](#-running)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👏 Acknowledgments](#-acknowledgments)

---


## 📍 Overview

Abstract

---

## 📦 Features

- Pedestrian Detection
- Crowd Detection
- TimeStamp of Max Detection
- Number of Detections/sec
- Color Customization
  

---


## 📂 Repository Structure

```sh
└── BeamEye/
    ├── BeamEye.py
    ├── detectionCode.py
    ├── detectionElements/
    │   ├── _detectionModel.pb
    │   ├── checkCrowd.py
    │   ├── drawing_tools.py
    │   ├── label_map_util.py
    │   ├── person_label_map.pbtxt
    │   ├── resizeVideo.py
    │   ├── string_int_label_map.proto
    │   ├── string_int_label_map_pb2.py
    ├── ScreenShots/
    ├── TestVideos/
    ├── uiAssets/
    │   ├── Lato/
    │   ├── Lato.ttf
    ├── uiElements/
    │   ├── SettingsWindow.py
    │   ├── sharedVariables.py
    │   ├── tkVideoPlayer.py
    │   ├── uiHandler.py
    │   └── userSettings.txt
    ├── videoFrames/
    ├── videoOut/
    └── videoResized/

```

---


## 🚀 Getting Started

***Dependencies***

Please ensure you have the following dependencies installed on your system:

`python`
`ffmpeg`

### 🔧 Installation

1. Clone the BeamEye repository:
```sh
git clone https://github.com/alshubati99/BeamEye
```

2. Change to the project directory:
```sh
cd BeamEye
```

3. Install the dependencies:
```sh
pip install -r requirements.txt
```

### 🤖 Running

```sh
python BeamEye.py
```



## 🤝 Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Submit Pull Requests](https://github.com/alshubati99/BeamEye/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github.com/alshubati99/BeamEye/discussions)**: Share your insights, provide feedback, or ask questions.
- **[Report Issues](https://github.com/alshubati99/BeamEye/issues)**: Submit bugs found or log feature requests for ALSHUBATI99.

#### *Contributing Guidelines*



1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a Git client.
   ```sh
   git clone <your-forked-repo-url>
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear and concise message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.

Once your PR is reviewed and approved, it will be merged into the main branch.


---

## 📄 License


This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## 👏 Acknowledgments

- List any resources, contributors, inspiration, etc. here.

[**Return**](#Top)

---

