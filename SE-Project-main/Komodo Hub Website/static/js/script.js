document.addEventListener('DOMContentLoaded', () => {
  // -------------------- USER DROPDOWN TOGGLE --------------------
  const userDropdownBtn = document.querySelector('.user-btn');
  const userDropdown = document.querySelector('.dropdown-menu'); // Ensure this matches your base.html
  
  if (userDropdownBtn && userDropdown) {
    // Toggle dropdown on button click
    userDropdownBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('show');
    });
  
    // Close dropdown if clicking outside of it
    window.addEventListener('click', (e) => {
      if (!userDropdown.contains(e.target) && !userDropdownBtn.contains(e.target)) {
        userDropdown.classList.remove('show');
      }
    });
  
    // Optional: Close dropdown on scroll
    window.addEventListener('scroll', () => {
      userDropdown.classList.remove('show');
    });
  }
  
  // -------------------- QUOTES CAROUSEL --------------------
  let slideIndex = 0;
  
  function showSlides(n) {
    const slides = document.querySelectorAll('.quote-slide');
    if (!slides.length) return;
  
    if (n >= slides.length) slideIndex = 0;
    if (n < 0) slideIndex = slides.length - 1;
  
    slides.forEach(slide => slide.classList.remove('active'));
    slides[slideIndex].classList.add('active');
  }
  
  function changeQuote(n) {
    slideIndex += n;
    showSlides(slideIndex);
  }
  
  if (document.querySelector('.quote-slide')) {
    showSlides(slideIndex);
    document.querySelectorAll('.carousel-btn.left').forEach(btn => {
      btn.addEventListener('click', () => changeQuote(-1));
    });
    document.querySelectorAll('.carousel-btn.right').forEach(btn => {
      btn.addEventListener('click', () => changeQuote(1));
    });
    setInterval(() => changeQuote(1), 7000);
  }
  
  // -------------------- IMAGE PREVIEW --------------------
  const mediaInput = document.getElementById('media');
  const imagePreview = document.getElementById('imagePreview');
  
  if (mediaInput && imagePreview) {
    mediaInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function (event) {
          imagePreview.innerHTML = `<img src="${event.target.result}" alt="Preview" style="max-height: 200px; border-radius: 5px;">`;
        };
        reader.readAsDataURL(file);
      } else {
        imagePreview.innerHTML = '';
      }
    });
  }
  
  // -------------------- FLASH MESSAGES AUTO DISMISS --------------------
  const flashMessages = document.querySelectorAll('.flash');
  flashMessages.forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transition = 'opacity 0.5s ease';
      setTimeout(() => {
        msg.style.display = 'none';
      }, 500);
    }, 5000);
  });
  
  // -------------------- ABOUT US - ACCORDION TOGGLE --------------------
  const toggleButtons = document.querySelectorAll('.toggle-btn');
  toggleButtons.forEach(button => {
    button.addEventListener('click', () => {
      const infoContent = button.closest('.info-box').querySelector('.info-content');
      const isActive = infoContent.classList.contains('active');
  
      // Close all accordion sections
      document.querySelectorAll('.info-content').forEach(content => content.classList.remove('active'));
      document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('rotate'));
  
      if (!isActive) {
        infoContent.classList.add('active');
        button.classList.add('rotate');
      }
    });
  });
  
  // -------------------- OPTIONAL: MOBILE MENU TOGGLE --------------------
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });
  }
});
