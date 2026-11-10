(function () {
  var canvas = document.getElementById("hero-canvas");
  var hero = document.querySelector(".hero");
  if (!canvas || !hero) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    hero.classList.add("no-webgl");
    return;
  }
  if (typeof THREE === "undefined") {
    hero.classList.add("no-webgl");
    return;
  }
  var gl;
  try {
    gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
  } catch (e) { gl = null; }
  if (!gl) {
    hero.classList.add("no-webgl");
    return;
  }

  hero.classList.add("webgl-on");
  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, powerPreference: "low-power" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(38, 2, 0.1, 100);
  camera.position.set(0, 0.15, 6.2);

  scene.add(new THREE.AmbientLight(0x7dd3a8, 0.35));
  var key = new THREE.DirectionalLight(0xffffff, 1.15);
  key.position.set(3, 4, 5);
  scene.add(key);
  var rim = new THREE.DirectionalLight(0x7dd3a8, 0.9);
  rim.position.set(-4, 1, -3);
  scene.add(rim);
  var fill = new THREE.PointLight(0x4e6a9a, 1.2, 20);
  fill.position.set(0, -2, 4);
  scene.add(fill);

  var group = new THREE.Group();
  scene.add(group);

  var ring = new THREE.Mesh(
    new THREE.TorusGeometry(1.55, 0.07, 16, 96),
    new THREE.MeshStandardMaterial({ color: 0x7dd3a8, metalness: 0.8, roughness: 0.25, emissive: 0x0b2a1c, emissiveIntensity: 0.4 })
  );
  group.add(ring);

  var ring2 = new THREE.Mesh(
    new THREE.TorusGeometry(1.9, 0.025, 12, 80),
    new THREE.MeshStandardMaterial({ color: 0xc9d4e5, metalness: 0.7, roughness: 0.35 })
  );
  ring2.rotation.x = Math.PI / 2.6;
  group.add(ring2);

  var disc = new THREE.Mesh(
    new THREE.CylinderGeometry(1.28, 1.28, 0.12, 64),
    new THREE.MeshStandardMaterial({ color: 0x1a2233, metalness: 0.6, roughness: 0.4 })
  );
  disc.rotation.x = Math.PI / 2;
  group.add(disc);

  var loader = new THREE.TextureLoader();
  loader.load("assets/logo.png", function (tex) {
    tex.colorSpace = THREE.SRGBColorSpace;
    var mat = new THREE.MeshStandardMaterial({
      map: tex, transparent: true, metalness: 0.15, roughness: 0.45,
      emissive: 0x7dd3a8, emissiveIntensity: 0.12
    });
    var badge = new THREE.Mesh(new THREE.CircleGeometry(1.12, 64), mat);
    badge.position.z = 0.08;
    group.add(badge);
    var badgeBack = new THREE.Mesh(new THREE.CircleGeometry(1.12, 64), mat);
    badgeBack.rotation.y = Math.PI;
    badgeBack.position.z = -0.08;
    group.add(badgeBack);
  }, undefined, function () { /* texture failed; metal disc still shows */ });

  var pGeo = new THREE.BufferGeometry();
  var count = 180;
  var pos = new Float32Array(count * 3);
  for (var i = 0; i < count; i++) {
    var a = Math.random() * Math.PI * 2;
    var r = 2.3 + Math.random() * 2.4;
    pos[i * 3] = Math.cos(a) * r;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 2.8;
    pos[i * 3 + 2] = Math.sin(a) * r * 0.6;
  }
  pGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  var points = new THREE.Points(
    pGeo,
    new THREE.PointsMaterial({ color: 0x7dd3a8, size: 0.035, transparent: true, opacity: 0.7 })
  );
  scene.add(points);

  group.position.set(1.7, 0.1, 0);

  var mx = 0, my = 0, tx = 0, ty = 0;
  window.addEventListener("pointermove", function (e) {
    tx = (e.clientX / window.innerWidth) * 2 - 1;
    ty = (e.clientY / window.innerHeight) * 2 - 1;
  }, { passive: true });

  function resize() {
    var w = hero.clientWidth;
    var h = hero.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(h, 1);
    camera.updateProjectionMatrix();
    // shift emblem right on wide screens, center on small
    group.position.x = w > 800 ? 1.7 : 0;
    group.position.y = w > 800 ? 0.1 : 0.55;
    group.scale.setScalar(w > 800 ? 1 : 0.82);
  }
  window.addEventListener("resize", resize);
  resize();

  var t0 = performance.now();
  var running = true;
  document.addEventListener("visibilitychange", function () {
    running = document.visibilityState === "visible";
    if (running) requestAnimationFrame(tick);
  });

  function tick(now) {
    if (!running) return;
    requestAnimationFrame(tick);
    var t = (now - t0) / 1000;
    mx += (tx - mx) * 0.04;
    my += (ty - my) * 0.04;
    group.rotation.y = t * 0.35 + mx * 0.4;
    group.rotation.x = 0.18 + my * 0.2;
    ring2.rotation.z = t * 0.2;
    points.rotation.y = t * 0.05;
    camera.position.x = mx * 0.25;
    camera.lookAt(0, 0.1, 0);
    renderer.render(scene, camera);
  }
  requestAnimationFrame(tick);

  canvas.addEventListener("webglcontextlost", function (e) {
    e.preventDefault();
    running = false;
    hero.classList.add("no-webgl");
  });
})();
