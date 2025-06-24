document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.getElementById("media");
    const imagePreview = document.getElementById("imagePreview");
  
    // Show live preview of uploaded image
    imageInput.addEventListener("change", function () {
      const file = this.files[0];
      if (file && file.type.startsWith("image/")) {
        const reader = new FileReader();
  
        reader.onload = function (e) {
          let img = imagePreview.querySelector("img");
          if (!img) {
            img = document.createElement("img");
            imagePreview.appendChild(img);
          }
  
          img.src = e.target.result;
          img.style.display = "block";
          img.style.animation = "fadeIn 0.5s ease";
        };
  
        reader.readAsDataURL(file);
      } else {
        imagePreview.innerHTML = "";
      }
    });
  
    // Optional: Basic client-side form validation
    const form = document.querySelector("form");
    form.addEventListener("submit", function (e) {
      const species = document.getElementById("species").value.trim();
      const location = document.getElementById("location").value.trim();
  
      if (!species || !location) {
        alert("Please fill in both species and location fields.");
        e.preventDefault();
      }
    });
  });
  
  // Optional: fade-in animation (can also go in CSS)
  const style = document.createElement("style");
  style.innerHTML = `
  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }
  `;
  document.head.appendChild(style);
  