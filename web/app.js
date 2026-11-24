// --- PARTICLE BACKGROUND ---
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const particles = [];
for (let i = 0; i < 50; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 2 + 1,
        dx: (Math.random() - 0.5) * 0.5,
        dy: (Math.random() - 0.5) * 0.5,
        alpha: Math.random() * 0.5 + 0.1
    });
}

function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
        p.x += p.dx;
        p.y += p.dy;
        if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(168, 85, 247, ${p.alpha})`;
        ctx.fill();
    });
    requestAnimationFrame(drawParticles);
}
drawParticles();

// --- MATTER.JS GRAVITY PHASE ---
const Engine = Matter.Engine,
      Render = Matter.Render,
      Runner = Matter.Runner,
      Bodies = Matter.Bodies,
      Composite = Matter.Composite;

const engine = Engine.create();
const elements = document.querySelectorAll('.physics-element');
const domBodies = [];

// Create static floor and walls
const floor = Bodies.rectangle(window.innerWidth/2, window.innerHeight + 25, window.innerWidth, 50, { isStatic: true });
const leftWall = Bodies.rectangle(-25, window.innerHeight/2, 50, window.innerHeight, { isStatic: true });
const rightWall = Bodies.rectangle(window.innerWidth + 25, window.innerHeight/2, 50, window.innerHeight, { isStatic: true });

Composite.add(engine.world, [floor, leftWall, rightWall]);

// Create physics bodies for UI elements
elements.forEach((el, index) => {
    const w = parseInt(el.getAttribute('data-width'));
    const h = parseInt(el.getAttribute('data-height'));
    
    // Start them high up with random x offsets
    const x = window.innerWidth / 2 + (Math.random() - 0.5) * 300;
    const y = -100 - (index * 100); 
    
    const body = Bodies.rectangle(x, y, w, h, {
        restitution: 0.8, // Bounciness
        friction: 0.1,
        angle: (Math.random() - 0.5) * 0.5
    });
    
    domBodies.push({ dom: el, body: body, w, h });
    Composite.add(engine.world, body);
});

Runner.run(Runner.create(), engine);

// Sync DOM elements to Physics bodies
function updateDOM() {
    if (!isPhase2) {
        domBodies.forEach(({ dom, body, w, h }) => {
            dom.style.width = w + 'px';
            dom.style.height = h + 'px';
            dom.style.left = (body.position.x - w/2) + 'px';
            dom.style.top = (body.position.y - h/2) + 'px';
            dom.style.transform = `rotate(${body.angle}rad)`;
        });
        requestAnimationFrame(updateDOM);
    }
}
updateDOM();

// --- PHASE 2 REORGANIZATION ---
let isPhase2 = false;

setTimeout(() => {
    isPhase2 = true;
    
    // Completely destroy the physics world to free up the buttons
    Matter.World.clear(engine.world);
    Matter.Engine.clear(engine);
    
    // Add CSS transition class
    elements.forEach(el => el.classList.add('phase-2-transition'));
    
    // Apply strict layout classes
    document.getElementById('logo').className = 'physics-element phase-2-transition layout-logo';
    document.getElementById('upload-btn').className = 'physics-element button phase-2-transition layout-upload';
    document.getElementById('sample-btn').className = 'physics-element button phase-2-transition layout-sample';
    document.getElementById('process-btn').className = 'physics-element button primary phase-2-transition layout-process';
    document.getElementById('output-area').className = 'physics-element panel phase-2-transition layout-panel';
    
}, 4000);

// --- INTERACTIONS ---
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn'); // Renamed for clarity
const outputContent = document.getElementById('output-content');
const placeholderText = document.querySelector('.placeholder-text');
const processBtn = document.getElementById('process-btn');
const sampleBtn = document.getElementById('sample-btn');
const spinner = document.getElementById('spinner');
const resultOverlay = document.getElementById('result-overlay');

const outputArea = document.getElementById('output-area');

let uploadedFile = null;

// Helper to convert base64 to Blob
async function base64ToBlob(base64) {
    const res = await fetch(base64);
    return await res.blob();
}

fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
        uploadedFile = e.target.files[0];
        const reader = new FileReader();
        reader.onload = function(event) {
            outputContent.style.backgroundImage = `url(${event.target.result})`;
            if (placeholderText) placeholderText.style.display = 'none';
            resultOverlay.classList.add('hidden');
            resultOverlay.innerHTML = '';
            outputArea.classList.add('visible'); // Show the panel
        }
        reader.readAsDataURL(uploadedFile);
    }
});

sampleBtn.addEventListener('click', async () => {
    try {
        spinner.classList.remove('hidden');
        outputArea.classList.add('visible'); // Show the panel early for the spinner
        const response = await fetch('/sample');
        const data = await response.json();
        spinner.classList.add('hidden');

        if (data.success) {
            outputContent.style.backgroundImage = `url(${data.image})`;
            if (placeholderText) placeholderText.style.display = 'none';
            resultOverlay.classList.add('hidden');
            
            // Convert to Blob so we can "upload" it
            const blob = await base64ToBlob(data.image);
            uploadedFile = new File([blob], data.filename, { type: 'image/png' });
            
            // Trigger process automatically
            processBtn.click();
        }
    } catch (err) {
        spinner.classList.add('hidden');
        alert("Error fetching sample: " + err.message);
    }
});

processBtn.addEventListener('click', async () => {
    if (!uploadedFile) {
        alert("Please upload an image or click 'Try Example'.");
        return;
    }
    
    // Show spinner
    spinner.classList.remove('hidden');
    resultOverlay.classList.add('hidden');
    
    // Create FormData
    const formData = new FormData();
    formData.append('image', uploadedFile);

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Hide spinner
        spinner.classList.add('hidden');

        if (data.success) {
            // Display result image (base64)
            outputContent.style.backgroundImage = `url(${data.result_image})`;
            
            // Update UI with class, face shape, and recommendation
            resultOverlay.innerHTML = `
                <div style="background: rgba(0,0,0,0.8); padding: 15px; border-radius: 12px; border: 1px solid #a855f7; backdrop-filter: blur(10px); text-align: left; max-width: 300px; margin: 0 auto;">
                    <div style="color: #a855f7; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid rgba(168,85,247,0.3); padding-bottom: 5px; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">
                        ✨ AI Stylist Report
                    </div>
                    <div style="color: #fff; font-size: 0.9rem; margin-bottom: 4px;">
                        <span style="opacity: 0.6;">Face Shape:</span> <b>${data.face_shape.toUpperCase()}</b>
                    </div>
                    <div style="color: #fff; font-size: 0.9rem; margin-bottom: 4px;">
                        <span style="opacity: 0.6;">Detected:</span> <b>${data.detected_hair}</b>
                    </div>
                    <div style="color: #4ade80; font-weight: bold; font-size: 0.95rem; margin-top: 10px; line-height: 1.3;">
                        Suggestion: ${data.recommended_style} hair is the perfect match for your ${data.face_shape} features!
                    </div>
                </div>
            `;
            resultOverlay.classList.remove('hidden');
        } else {
            alert("Error: " + data.error);
        }
    } catch (err) {
        spinner.classList.add('hidden');
        alert("Server Error: Make sure server.py is running on http://localhost:5000");
        console.error(err);
    }
});
