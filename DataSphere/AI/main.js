import * as THREE from "https://unpkg.com/three@0.152.2/build/three.module.js";
import { OrbitControls } from "https://unpkg.com/three@0.152.2/examples/jsm/controls/OrbitControls.js";

// Add debugging console logs
console.log("Three.js loaded:", THREE);
console.log("Starting Three.js setup...");

try {
  const scene = new THREE.Scene();
  console.log("Scene created:", scene);
  
  const camera = new THREE.PerspectiveCamera(60, innerWidth/innerHeight, 0.1, 1000);
  camera.position.z = 3;
  console.log("Camera created:", camera);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(innerWidth, innerHeight);
  console.log("Renderer created:", renderer);
  
  document.body.appendChild(renderer.domElement);
  console.log("Canvas added to DOM:", renderer.domElement);

  // Use OctahedronGeometry instead of SphereGeometry
  const octahedron = new THREE.Mesh(
    new THREE.OctahedronGeometry(1, 0), // radius 1, detail 0
    new THREE.MeshNormalMaterial()
  );
  scene.add(octahedron);
  console.log("Octahedron created and added to scene:", octahedron);

  const controls = new OrbitControls(camera, renderer.domElement);
  console.log("Controls created:", controls);

  addEventListener("resize", () => {
    camera.aspect = innerWidth/innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
    console.log("Window resized");
  });

  function animate() {
    requestAnimationFrame(animate);
    octahedron.rotation.y += 0.01;
    renderer.render(scene, camera);
  }
  
  console.log("Starting animation loop...");
  animate();
  
} catch (error) {
  console.error("Error in Three.js setup:", error);
}
