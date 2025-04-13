document.addEventListener('DOMContentLoaded', function() {
    // Create spotlight effect
    const spotlight = document.createElement('div');
    spotlight.className = 'spotlight';
    document.body.appendChild(spotlight);
    
    document.addEventListener('mousemove', e => {
        const { clientX, clientY } = e;
        const x = (clientX / window.innerWidth) * 100;
        const y = (clientY / window.innerHeight) * 100;
        spotlight.style.setProperty('--x', `${x}%`);
        spotlight.style.setProperty('--y', `${y}%`);
    });
    
    // Create particles
    for (let i = 0; i < 30; i++) {
        createParticle();
    }
    
    // Add shooting stars effect
    setInterval(() => {
        createShootingStar();
    }, 2000);
    
    // Add 3D tilt effect on feature items
    const cards = document.querySelectorAll('.feature-item');
    cards.forEach(card => {
        card.addEventListener('mousemove', handleTilt);
        card.addEventListener('mouseleave', resetTilt);
    });
});

function createParticle() {
    const particles = document.querySelector('.particles');
    if (!particles) {
        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'particles';
        document.body.appendChild(particlesContainer);
        setTimeout(() => createParticle(), 100);
        return;
    }
    
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // Random position
    particle.style.left = Math.random() * 100 + 'vw';
    particle.style.top = Math.random() * 100 + 'vh';
    
    // Random size
    const size = Math.random() * 6 + 2;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    
    // Random animation duration
    const duration = Math.random() * 20 + 10;
    particle.style.animationDuration = duration + 's';
    
    // Random delay
    const delay = Math.random() * 10;
    particle.style.animationDelay = delay + 's';
    
    particles.appendChild(particle);
    
    // Reset after animation complete
    setTimeout(() => {
        particle.remove();
        createParticle();
    }, (duration + delay) * 1000);
}

function createShootingStar() {
    const star = document.createElement('div');
    star.className = 'shooting-star';
    star.style.left = Math.random() * 100 + 'vw';
    star.style.top = Math.random() * 30 + 'vh';
    document.body.appendChild(star);
    
    setTimeout(() => {
        star.remove();
    }, 1000);
}

function handleTilt(e) {
    const card = this;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const tiltX = (y - centerY) / 10;
    const tiltY = (centerX - x) / 10;
    
    card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.05, 1.05, 1.05)`;
}

function resetTilt() {
    this.style.transform = '';
}