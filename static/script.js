// Show loading animation
function showLoadingAnimation() {
    document.getElementById('loading-animation').style.display = 'block';
}

// Hide loading animation
function hideLoadingAnimation() {
    document.getElementById('loading-animation').style.display = 'none';
}

// Example: Show loading animation when moving between pages
document.addEventListener('DOMContentLoaded', function() {
    // Show loading animation before page content is loaded
    showLoadingAnimation();
});

// Example: Hide loading animation when page content is fully loaded
window.addEventListener('load', function() {
    // Hide loading animation after page content is loaded
    hideLoadingAnimation();
});


// slide show


const sliderContainer = document.querySelector(".hero");
const slides = sliderContainer.querySelectorAll(".content");
let currentSlide = 0;

function showSlide(n) {
    gsap.from(slides[currentSlide].querySelector("h1"), { y: 50, opacity: 0, duration: 0.5 });
    slides.forEach((slide) => {
        slide.classList.remove("active");
    });
    slides[n].classList.add("active");
    gsap.to(slides[n].querySelector("h1"), { y: 0, opacity: 1, duration: 0.5, delay: 0.5 });
    currentSlide = n;
}
function autoplay() {
    currentSlide++;
    if (currentSlide >= slides.length) {
        currentSlide = 0;
    }
    showSlide(currentSlide);
}

const intervalId = setInterval(autoplay, 3000);

document.addEventListener("DOMContentLoaded", function() {
    const nav = document.getElementById("mainNav");
    const navOffsetTop = nav.offsetTop; // Distance from top of the document

    // Function to add/remove 'fixed' class based on scroll position
    function toggleFixedNav() {
        if (window.pageYOffset > navOffsetTop) {
            nav.classList.add("fixed");
        } else {
            nav.classList.remove("fixed");
        }
    }

    // Event listener for scroll events
    window.addEventListener("scroll", toggleFixedNav);
});