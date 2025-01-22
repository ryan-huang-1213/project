document.addEventListener("DOMContentLoaded", () => {
  fetch("/list-files")
    .then((response) => response.json())
    .then((files) => {
      const fileList = document.getElementById("files");
      files.forEach((file) => {
        const li = document.createElement("li");
        li.textContent = file;
        li.addEventListener("click", () => loadFile(file));
        fileList.appendChild(li);
      });
    });
});

function loadFile(file) {
  fetch(`/read-file?file=${file}`)
    .then((response) => response.text())
    .then((code) => {
      document.getElementById("code").textContent = code;
      runFile(file);
    });
}

function runFile(file) {
  fetch(`/run-file?file=${file}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error("Error:", data.details);
      } else {
        document.getElementById("output-image").src = data.imagePath;
      }
    })
    .catch((error) => console.error("Error:", error));
}
