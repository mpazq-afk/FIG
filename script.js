// Sticky Header
const header = document.getElementById('header');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Mobile Mobile Menu Toggle
const mobileToggle = document.querySelector('.mobile-toggle');
const nav = document.querySelector('.nav');

mobileToggle.addEventListener('click', () => {
    nav.classList.toggle('active');
    const icon = mobileToggle.querySelector('i');
    if (nav.classList.contains('active')) {
        icon.classList.remove('fa-bars');
        icon.classList.add('fa-xmark');
    } else {
        icon.classList.remove('fa-xmark');
        icon.classList.add('fa-bars');
    }
});

// Close mobile menu when clicking a link
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        nav.classList.remove('active');
        const icon = mobileToggle.querySelector('i');
        icon.classList.remove('fa-xmark');
        icon.classList.add('fa-bars');
    });
});

// Implementation of simple scroll reveal animation (Intersection Observer)
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.15
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Select all sections and cards to animate
const elementsToAnimate = document.querySelectorAll('.section-header, .about-text, .hof-card, .division-card, .apply-info, .apply-form-container');

elementsToAnimate.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(el);
});

// Form submission mock
const applyForm = document.querySelector('.apply-form');
if (applyForm) {
    applyForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const btn = applyForm.querySelector('button[type="submit"]');
        const originalText = btn.textContent;

        btn.textContent = 'Enviando...';
        btn.style.opacity = '0.7';

        // Mock API call delay
        setTimeout(() => {
            btn.textContent = '¡Postulación Enviada!';
            btn.style.backgroundColor = '#25D366';
            btn.style.color = '#fff';
            btn.style.opacity = '1';

            setTimeout(() => {
                applyForm.reset();
                btn.textContent = originalText;
                btn.style.backgroundColor = '';
                btn.style.color = '';
            }, 3000);
        }, 1500);
    });
}

// Dynamic Text Typing Animation
const dynamicText = document.querySelector('.dynamic-text');
const staticText = document.querySelector('.static-text');

let step = 0;
let text = "la Élite";

function typeEffect() {
    if (!dynamicText || !staticText) return;

    let typeSpeed = 100;

    if (step === 0) {
        // waiting after la Élite
        typeSpeed = 2000;
        step = 1;
    }
    else if (step === 1) {
        // deleting la Élite
        text = text.substring(0, text.length - 1);
        dynamicText.textContent = text;
        typeSpeed = 50;
        if (text === "") step = 2;
    }
    else if (step === 2) {
        // typing los Cracks
        const target = "los Cracks";
        text = target.substring(0, text.length + 1);
        dynamicText.textContent = text;
        typeSpeed = 100;
        if (text === target) step = 3;
    }
    else if (step === 3) {
        // waiting after los Cracks
        typeSpeed = 2000;
        step = 4;
    }
    else if (step === 4) {
        // Append static text to dynamic text for fast full delete
        if (staticText.textContent !== "") {
            text = text + staticText.textContent;
            dynamicText.textContent = text;
            staticText.textContent = "";
        }
        // super fast delete
        text = text.substring(0, text.length - 1);
        dynamicText.textContent = text;
        typeSpeed = 15;
        if (text === "") step = 5;
    }
    else if (step === 5) {
        // typing una comunidad
        const target = "una comunidad";
        text = target.substring(0, text.length + 1);
        dynamicText.textContent = text;
        typeSpeed = 100;
        if (text === target) step = 6;
    }
    else if (step === 6) {
        // waiting after una comunidad
        typeSpeed = 2000;
        step = 7;
    }
    else if (step === 7) {
        // deleting una comunidad
        text = text.substring(0, text.length - 1);
        dynamicText.textContent = text;
        typeSpeed = 15;
        if (text === "") step = 8;
    }
    else if (step === 8) {
        // Restore static text immediately before typing la Elite
        if (staticText.textContent === "") {
            staticText.textContent = " del Mañana";
        }
        // typing la Élite
        const target = "la Élite";
        text = target.substring(0, text.length + 1);
        dynamicText.textContent = text;
        typeSpeed = 100;
        if (text === target) step = 0;
    }

    setTimeout(typeEffect, typeSpeed);
}

// Start typing effect on load
if (dynamicText && staticText) {
    document.addEventListener("DOMContentLoaded", () => {
        dynamicText.textContent = "la Élite";
        staticText.textContent = " del Mañana";
        setTimeout(typeEffect, 2000);
    });
}

// Form Submission to Google Sheets
const scriptURL = 'https://script.google.com/macros/s/AKfycbzKzdDIjRO4ftsKSFHSE9c6RlfBRuWAgHGtVKyK92ZTR61Zl6V9AaqASP-P9yesw99S/exec';
const form = document.querySelector('.apply-form');
const submitBtn = document.getElementById('submit-btn');
const modal = document.getElementById('success-modal');
const closeModalBtn = document.querySelector('.close-modal');

if (form) {
    form.addEventListener('submit', e => {
        e.preventDefault();

        // Show loading state
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Enviando...';
        submitBtn.classList.add('loading');

        fetch(scriptURL, {
            method: 'POST',
            body: new FormData(form)
        })
            .then(response => {
                // Restore button
                submitBtn.textContent = originalText;
                submitBtn.classList.remove('loading');

                // Show success modal
                modal.classList.add('show');
                form.reset(); // clear form
            })
            .catch(error => {
                console.error('Error!', error.message);
                submitBtn.textContent = originalText;
                submitBtn.classList.remove('loading');
                alert('Hubo un error al enviar tu postulación. Por favor intenta de nuevo más tarde.');
            });
    });
}

// Modal handling
if (closeModalBtn && modal) {
    closeModalBtn.addEventListener('click', () => {
        modal.classList.remove('show');
    });

    // Close when clicking outside of modal
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });
}
