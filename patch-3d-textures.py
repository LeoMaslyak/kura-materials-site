#!/usr/bin/env python3
"""Patch Three.js product showcase with improved textures and hover captions."""

import re, sys

with open('index.html', 'r') as f:
    content = f.read()

replacements = 0

# ============================================================
# 1. Replace the entire createProduct function + material setup
# ============================================================

old_create_product = '''            // Create products with realistic 3D shapes
            const productMeshes = [];
            
            // Helper function to create product geometries
            function createProduct(index, product) {
                const material = new THREE.MeshStandardMaterial({
                    color: product.color,
                    roughness: 0.7,
                    metalness: 0.1,
                    emissive: product.color,
                    emissiveIntensity: 0.05
                });

                let mesh;
                
                switch(index) {
                    case 0: // Eco-Concrete Blocks - rectangular blocks with beveled edges
                        const blockGeometry = new THREE.BoxGeometry(4, 6, 4, 2, 2, 2);
                        mesh = new THREE.Mesh(blockGeometry, material);
                        break;
                        
                    case 1: // Sustainable Aggregates - pile of small rocks
                        const aggregateGroup = new THREE.Group();
                        for (let i = 0; i < 25; i++) {
                            const rockSize = Math.random() * 0.5 + 0.3;
                            const rockGeom = new THREE.DodecahedronGeometry(rockSize);
                            const rockMesh = new THREE.Mesh(rockGeom, material);
                            rockMesh.position.set(
                                (Math.random() - 0.5) * 3,
                                Math.random() * 2,
                                (Math.random() - 0.5) * 3
                            );
                            rockMesh.castShadow = true;
                            rockMesh.receiveShadow = true;
                            aggregateGroup.add(rockMesh);
                        }
                        mesh = aggregateGroup;
                        break;
                        
                    case 2: // Green Paving Stones - hexagonal paver
                        const paverGeometry = new THREE.CylinderGeometry(2.5, 2.5, 0.8, 6);
                        mesh = new THREE.Mesh(paverGeometry, material);
                        break;
                        
                    case 3: // Low-Carbon Bricks - stack of bricks
                        const brickGroup = new THREE.Group();
                        for (let i = 0; i < 4; i++) {
                            const brickGeom = new THREE.BoxGeometry(4, 2, 2);
                            const brickMesh = new THREE.Mesh(brickGeom, material);
                            brickMesh.position.y = i * 2.1;
                            brickMesh.castShadow = true;
                            brickMesh.receiveShadow = true;
                            brickGroup.add(brickMesh);
                        }
                        mesh = brickGroup;
                        break;
                        
                    case 4: // Geopolymer Cement - barrel/cylinder
                        const barrelGroup = new THREE.Group();
                        const barrelBody = new THREE.Mesh(
                            new THREE.CylinderGeometry(1.2, 1.2, 7, 16),
                            material
                        );
                        barrelBody.castShadow = true;
                        barrelBody.receiveShadow = true;
                        barrelGroup.add(barrelBody);
                        
                        // Add metal bands
                        const bandMaterial = new THREE.MeshStandardMaterial({
                            color: 0x333333,
                            roughness: 0.3,
                            metalness: 0.8
                        });
                        for (let i = -2; i <= 2; i++) {
                            const band = new THREE.Mesh(
                                new THREE.CylinderGeometry(1.25, 1.25, 0.2, 16),
                                bandMaterial
                            );
                            band.position.y = i * 1.5;
                            barrelGroup.add(band);
                        }
                        mesh = barrelGroup;
                        break;
                        
                    case 5: // Recycled Fill Material - pile of chunky spheres
                        const fillGroup = new THREE.Group();
                        for (let i = 0; i < 35; i++) {
                            const chunkSize = Math.random() * 0.6 + 0.4;
                            const chunkGeom = new THREE.SphereGeometry(chunkSize, 6, 6);
                            const chunkMesh = new THREE.Mesh(chunkGeom, material);
                            chunkMesh.position.set(
                                (Math.random() - 0.5) * 4,
                                Math.random() * 2.5,
                                (Math.random() - 0.5) * 4
                            );
                            chunkMesh.castShadow = true;
                            chunkMesh.receiveShadow = true;
                            fillGroup.add(chunkMesh);
                        }
                        mesh = fillGroup;
                        break;
                        
                    case 6: // Industrial Sand - cone/pyramid pile
                        const coneGeometry = new THREE.ConeGeometry(2.5, 4.5, 32);
                        mesh = new THREE.Mesh(coneGeometry, material);
                        break;
                        
                    default:
                        const defaultGeometry = new THREE.BoxGeometry(4, 6, 4);
                        mesh = new THREE.Mesh(defaultGeometry, material);
                }
                
                mesh.position.set(product.pos[0], product.pos[1], product.pos[2]);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                mesh.userData = { 
                    name: product.name, 
                    description: product.desc,
                    originalColor: product.color,
                    index: index
                };
                
                return mesh;
            }'''

new_create_product = '''            // Create products with realistic 3D shapes
            const productMeshes = [];

            // --- Procedural texture generators ---
            function createNoiseTexture(baseColor, variation, size) {
                const canvas = document.createElement('canvas');
                canvas.width = size || 256;
                canvas.height = size || 256;
                const ctx = canvas.getContext('2d');
                const r = (baseColor >> 16) & 0xff;
                const g = (baseColor >> 8) & 0xff;
                const b = baseColor & 0xff;
                const imgData = ctx.createImageData(canvas.width, canvas.height);
                for (let i = 0; i < imgData.data.length; i += 4) {
                    const v = (Math.random() - 0.5) * variation;
                    imgData.data[i]     = Math.min(255, Math.max(0, r + v));
                    imgData.data[i + 1] = Math.min(255, Math.max(0, g + v));
                    imgData.data[i + 2] = Math.min(255, Math.max(0, b + v));
                    imgData.data[i + 3] = 255;
                }
                ctx.putImageData(imgData, 0, 0);
                const tex = new THREE.CanvasTexture(canvas);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                return tex;
            }

            function createRoughnessMap(baseVal, variation, size) {
                const canvas = document.createElement('canvas');
                canvas.width = size || 256;
                canvas.height = size || 256;
                const ctx = canvas.getContext('2d');
                const imgData = ctx.createImageData(canvas.width, canvas.height);
                const base = Math.round(baseVal * 255);
                const vr = Math.round(variation * 255);
                for (let i = 0; i < imgData.data.length; i += 4) {
                    const val = Math.min(255, Math.max(0, base + (Math.random() - 0.5) * vr));
                    imgData.data[i] = imgData.data[i+1] = imgData.data[i+2] = val;
                    imgData.data[i + 3] = 255;
                }
                ctx.putImageData(imgData, 0, 0);
                const tex = new THREE.CanvasTexture(canvas);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                return tex;
            }

            function createBumpMap(intensity, size) {
                const canvas = document.createElement('canvas');
                canvas.width = size || 256;
                canvas.height = size || 256;
                const ctx = canvas.getContext('2d');
                const imgData = ctx.createImageData(canvas.width, canvas.height);
                for (let i = 0; i < imgData.data.length; i += 4) {
                    const val = Math.round(Math.random() * intensity * 255);
                    imgData.data[i] = imgData.data[i+1] = imgData.data[i+2] = val;
                    imgData.data[i + 3] = 255;
                }
                ctx.putImageData(imgData, 0, 0);
                const tex = new THREE.CanvasTexture(canvas);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                return tex;
            }

            function createConcreteTexture(baseColor) {
                const canvas = document.createElement('canvas');
                canvas.width = 512;
                canvas.height = 512;
                const ctx = canvas.getContext('2d');
                const r = (baseColor >> 16) & 0xff;
                const g = (baseColor >> 8) & 0xff;
                const b = baseColor & 0xff;
                ctx.fillStyle = `rgb(${r},${g},${b})`;
                ctx.fillRect(0, 0, 512, 512);
                for (let i = 0; i < 800; i++) {
                    const x = Math.random() * 512;
                    const y = Math.random() * 512;
                    const size = Math.random() * 4 + 1;
                    const shade = Math.random() * 60 - 30;
                    ctx.fillStyle = `rgb(${Math.min(255,Math.max(0,r+shade))},${Math.min(255,Math.max(0,g+shade))},${Math.min(255,Math.max(0,b+shade))})`;
                    ctx.beginPath();
                    ctx.arc(x, y, size, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.strokeStyle = `rgba(${Math.max(0,r-40)},${Math.max(0,g-40)},${Math.max(0,b-40)},0.3)`;
                ctx.lineWidth = 0.5;
                for (let i = 0; i < 5; i++) {
                    ctx.beginPath();
                    let cx = Math.random() * 512, cy = Math.random() * 512;
                    ctx.moveTo(cx, cy);
                    for (let j = 0; j < 8; j++) {
                        cx += (Math.random() - 0.5) * 60;
                        cy += (Math.random() - 0.5) * 60;
                        ctx.lineTo(cx, cy);
                    }
                    ctx.stroke();
                }
                const tex = new THREE.CanvasTexture(canvas);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                return tex;
            }

            function createBrickTexture(baseColor) {
                const canvas = document.createElement('canvas');
                canvas.width = 512;
                canvas.height = 512;
                const ctx = canvas.getContext('2d');
                const r = (baseColor >> 16) & 0xff;
                const g = (baseColor >> 8) & 0xff;
                const b = baseColor & 0xff;
                ctx.fillStyle = `rgb(${r},${g},${b})`;
                ctx.fillRect(0, 0, 512, 512);
                for (let i = 0; i < 400; i++) {
                    const x = Math.random() * 512;
                    const y = Math.random() * 512;
                    const s = Math.random() * 3 + 0.5;
                    const d = Math.random() * 30 - 15;
                    ctx.fillStyle = `rgb(${Math.min(255,Math.max(0,r+d))},${Math.min(255,Math.max(0,g+d))},${Math.min(255,Math.max(0,b+d))})`;
                    ctx.beginPath();
                    ctx.arc(x, y, s, 0, Math.PI * 2);
                    ctx.fill();
                }
                const tex = new THREE.CanvasTexture(canvas);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                return tex;
            }

            function createSandTexture(baseColor) {
                const canvas = document.createElement('canvas');
                canvas.width = 512;
                canvas.height = 512;
                const ctx = canvas.getContext('2d');
                const r = (baseColor >> 16) & 0xff;
                const g = (baseColor >> 8) & 0xff;
                const b = baseColor & 0xff;
                ctx.fillStyle = `rgb(${r},${g},${b})`;
                ctx.fillRect(0, 0, 512, 512);
                for (let i = 0; i < 3000; i++) {
                    const x = Math.random() * 512;
                    const y = Math.random() * 512;
                    const d = Math.random() * 40 - 20;
                    ctx.fillStyle = `rgb(${Math.min(255,Math.max(0,r+d))},${Math.min(255,Math.max(0,g+d))},${Math.min(255,Math.max(0,b+d))})`;
                    ctx.fillRect(x, y, 1.5, 1.5);
                }
                const tex = new THREE.CanvasTexture(canvas);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                return tex;
            }

            // Material presets per product type
            const materialPresets = [
                { roughness: 0.85, metalness: 0.02, bumpScale: 0.08, texGen: createConcreteTexture },
                { roughness: 0.95, metalness: 0.0, bumpScale: 0.12, texGen: createNoiseTexture, texVar: 60 },
                { roughness: 0.6, metalness: 0.05, bumpScale: 0.04, texGen: createConcreteTexture },
                { roughness: 0.8, metalness: 0.0, bumpScale: 0.06, texGen: createBrickTexture },
                { roughness: 0.4, metalness: 0.05, bumpScale: 0.02, texGen: createConcreteTexture },
                { roughness: 0.9, metalness: 0.0, bumpScale: 0.1, texGen: createNoiseTexture, texVar: 50 },
                { roughness: 0.7, metalness: 0.1, bumpScale: 0.03, texGen: createSandTexture }
            ];

            function createProduct(index, product) {
                const preset = materialPresets[index] || materialPresets[0];
                const colorMap = preset.texGen === createNoiseTexture
                    ? createNoiseTexture(product.color, preset.texVar || 40, 256)
                    : preset.texGen(product.color);
                const roughnessMap = createRoughnessMap(preset.roughness, 0.15, 256);
                const bumpMap = createBumpMap(0.6, 256);

                const material = new THREE.MeshStandardMaterial({
                    map: colorMap,
                    color: product.color,
                    roughness: preset.roughness,
                    roughnessMap: roughnessMap,
                    metalness: preset.metalness,
                    bumpMap: bumpMap,
                    bumpScale: preset.bumpScale,
                    emissive: product.color,
                    emissiveIntensity: 0.05
                });

                let mesh;
                
                switch(index) {
                    case 0: {
                        const blockGroup = new THREE.Group();
                        const block1 = new THREE.Mesh(new THREE.BoxGeometry(4, 3, 4, 4, 4, 4), material);
                        block1.position.y = 0;
                        block1.castShadow = true;
                        block1.receiveShadow = true;
                        blockGroup.add(block1);
                        const block2Mat = material.clone();
                        block2Mat.color.offsetHSL(0, 0, -0.05);
                        const block2 = new THREE.Mesh(new THREE.BoxGeometry(3.8, 2.5, 3.8, 4, 4, 4), block2Mat);
                        block2.position.set(0.3, 3, 0.2);
                        block2.rotation.y = 0.1;
                        block2.castShadow = true;
                        block2.receiveShadow = true;
                        blockGroup.add(block2);
                        mesh = blockGroup;
                        break;
                    }
                    case 1: {
                        const aggregateGroup = new THREE.Group();
                        for (let i = 0; i < 30; i++) {
                            const rockSize = Math.random() * 0.6 + 0.25;
                            const detail = Math.random() > 0.5 ? 1 : 0;
                            const rockGeom = new THREE.DodecahedronGeometry(rockSize, detail);
                            const rockMat = material.clone();
                            rockMat.color.offsetHSL(0, (Math.random()-0.5)*0.1, (Math.random()-0.5)*0.1);
                            const rockMesh = new THREE.Mesh(rockGeom, rockMat);
                            const angle = Math.random() * Math.PI * 2;
                            const dist = Math.random() * 1.8;
                            rockMesh.position.set(
                                Math.cos(angle) * dist,
                                Math.random() * 2.2,
                                Math.sin(angle) * dist
                            );
                            rockMesh.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
                            rockMesh.castShadow = true;
                            rockMesh.receiveShadow = true;
                            aggregateGroup.add(rockMesh);
                        }
                        mesh = aggregateGroup;
                        break;
                    }
                    case 2: {
                        const paverGroup = new THREE.Group();
                        const mainPaver = new THREE.Mesh(
                            new THREE.CylinderGeometry(2.5, 2.5, 1, 6),
                            material
                        );
                        mainPaver.castShadow = true;
                        mainPaver.receiveShadow = true;
                        paverGroup.add(mainPaver);
                        const accentMat = material.clone();
                        accentMat.color.offsetHSL(0.02, 0, -0.08);
                        const offsets = [[2.8,0,1.6],[-2.8,0,1.6],[2.8,0,-1.6]];
                        offsets.forEach(off => {
                            const p = new THREE.Mesh(
                                new THREE.CylinderGeometry(1.2, 1.2, 1, 6),
                                accentMat
                            );
                            p.position.set(off[0], off[1], off[2]);
                            p.castShadow = true;
                            p.receiveShadow = true;
                            paverGroup.add(p);
                        });
                        mesh = paverGroup;
                        break;
                    }
                    case 3: {
                        const brickGroup = new THREE.Group();
                        const brickW = 3.6, brickH = 1.6, brickD = 1.8, gap = 0.15;
                        for (let row = 0; row < 4; row++) {
                            const offset = (row % 2) * (brickW * 0.5 + gap * 0.5);
                            for (let col = 0; col < 2; col++) {
                                const bMat = material.clone();
                                bMat.color.offsetHSL(0, (Math.random()-0.5)*0.05, (Math.random()-0.5)*0.06);
                                const brickGeom = new THREE.BoxGeometry(brickW, brickH, brickD, 2, 2, 2);
                                const brickMesh = new THREE.Mesh(brickGeom, bMat);
                                brickMesh.position.set(
                                    col * (brickW + gap) - (brickW * 0.5) + offset - 1,
                                    row * (brickH + gap),
                                    0
                                );
                                brickMesh.castShadow = true;
                                brickMesh.receiveShadow = true;
                                brickGroup.add(brickMesh);
                            }
                        }
                        mesh = brickGroup;
                        break;
                    }
                    case 4: {
                        const barrelGroup = new THREE.Group();
                        const barrelBody = new THREE.Mesh(
                            new THREE.CylinderGeometry(1.3, 1.2, 7, 24),
                            material
                        );
                        barrelBody.castShadow = true;
                        barrelBody.receiveShadow = true;
                        barrelGroup.add(barrelBody);
                        const bandMaterial = new THREE.MeshStandardMaterial({
                            color: 0x444444,
                            roughness: 0.25,
                            metalness: 0.9,
                            emissive: 0x222222,
                            emissiveIntensity: 0.1
                        });
                        [-2.5, -0.8, 0.8, 2.5].forEach(y => {
                            const band = new THREE.Mesh(
                                new THREE.CylinderGeometry(1.35, 1.35, 0.18, 24),
                                bandMaterial
                            );
                            band.position.y = y;
                            band.castShadow = true;
                            barrelGroup.add(band);
                        });
                        const lidMat = bandMaterial.clone();
                        lidMat.color.set(0x555555);
                        const lid = new THREE.Mesh(
                            new THREE.CylinderGeometry(1.3, 1.3, 0.15, 24),
                            lidMat
                        );
                        lid.position.y = 3.55;
                        barrelGroup.add(lid);
                        mesh = barrelGroup;
                        break;
                    }
                    case 5: {
                        const fillGroup = new THREE.Group();
                        for (let i = 0; i < 40; i++) {
                            const chunkSize = Math.random() * 0.55 + 0.3;
                            const chunkGeom = new THREE.SphereGeometry(chunkSize, 5, 5);
                            const cMat = material.clone();
                            cMat.color.offsetHSL(0, (Math.random()-0.5)*0.08, (Math.random()-0.5)*0.12);
                            const chunkMesh = new THREE.Mesh(chunkGeom, cMat);
                            const angle = Math.random() * Math.PI * 2;
                            const dist = Math.random() * 2.2;
                            const height = Math.max(0, 2 - dist * 0.8) * Math.random() + chunkSize * 0.5;
                            chunkMesh.position.set(
                                Math.cos(angle) * dist,
                                height,
                                Math.sin(angle) * dist
                            );
                            chunkMesh.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, 0);
                            chunkMesh.castShadow = true;
                            chunkMesh.receiveShadow = true;
                            fillGroup.add(chunkMesh);
                        }
                        mesh = fillGroup;
                        break;
                    }
                    case 6: {
                        const sandGroup = new THREE.Group();
                        const mainCone = new THREE.Mesh(
                            new THREE.ConeGeometry(2.8, 5, 48, 4),
                            material
                        );
                        mainCone.castShadow = true;
                        mainCone.receiveShadow = true;
                        sandGroup.add(mainCone);
                        const grainMat = material.clone();
                        grainMat.color.offsetHSL(0, 0, -0.05);
                        for (let i = 0; i < 20; i++) {
                            const grain = new THREE.Mesh(
                                new THREE.SphereGeometry(Math.random() * 0.15 + 0.05, 4, 4),
                                grainMat
                            );
                            const a = Math.random() * Math.PI * 2;
                            const d = 2.5 + Math.random() * 1.5;
                            grain.position.set(Math.cos(a)*d, -2.3, Math.sin(a)*d);
                            sandGroup.add(grain);
                        }
                        mesh = sandGroup;
                        break;
                    }
                    default: {
                        const defaultGeometry = new THREE.BoxGeometry(4, 6, 4);
                        mesh = new THREE.Mesh(defaultGeometry, material);
                    }
                }
                
                mesh.position.set(product.pos[0], product.pos[1], product.pos[2]);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                mesh.userData = { 
                    name: product.name, 
                    description: product.desc,
                    originalColor: product.color,
                    index: index
                };
                
                return mesh;
            }'''

if old_create_product in content:
    content = content.replace(old_create_product, new_create_product)
    replacements += 1
    print("✅ 1. Replaced createProduct with procedural textures")
else:
    print("❌ 1. Could not find createProduct block")

# ============================================================
# 2. Improve lighting
# ============================================================

old_lights = '''            const directionalLight3 = new THREE.DirectionalLight(0x4A7C59, 0.2);
            directionalLight3.position.set(0, -10, 10);
            scene.add(directionalLight3);'''

new_lights = '''            const directionalLight3 = new THREE.DirectionalLight(0x4A7C59, 0.2);
            directionalLight3.position.set(0, -10, 10);
            scene.add(directionalLight3);

            // Rim light for edge definition
            const rimLight = new THREE.DirectionalLight(0xffffff, 0.15);
            rimLight.position.set(0, 5, -15);
            scene.add(rimLight);

            // Soft hemisphere light for natural fill
            const hemiLight = new THREE.HemisphereLight(0xffeedd, 0x222222, 0.25);
            scene.add(hemiLight);'''

if old_lights in content:
    content = content.replace(old_lights, new_lights)
    replacements += 1
    print("✅ 2. Added rim + hemisphere lights")
else:
    print("❌ 2. Could not find lighting block")

# ============================================================
# 3. Fix click handler for Groups
# ============================================================

old_click = '''                    if (intersects.length > 0) {
                        const product = intersects[0].object.userData;
                        productName.textContent = product.name;
                        productDescription.textContent = product.description;
                        infoPanel.style.display = 'block';'''

new_click = '''                    if (intersects.length > 0) {
                        let clickObj = intersects[0].object;
                        while (clickObj.parent && !clickObj.userData.name && clickObj.parent.type !== 'Scene') {
                            clickObj = clickObj.parent;
                        }
                        const product = clickObj.userData;
                        if (!product.name) return;
                        productName.textContent = product.name;
                        productDescription.textContent = product.description;
                        infoPanel.style.display = 'block';'''

if old_click in content:
    content = content.replace(old_click, new_click)
    replacements += 1
    print("✅ 3. Fixed click handler for Group traversal")
else:
    print("❌ 3. Could not find click handler block")

# ============================================================
# 4. Enhance hover label styling
# ============================================================

old_label = '''    <div id="product-label" style="position: absolute; display: none; background: rgba(15,15,15,0.95); padding: 16px 24px; border-radius: 12px; pointer-events: none; transition: opacity 0.3s; z-index: 9999; border: 2px solid #C87533; backdrop-filter: blur(10px); max-width: 320px;">
        <h4 style="color: #C87533; font-weight: 700; margin: 0 0 8px 0; font-size: 16px; font-family: 'Plus Jakarta Sans', sans-serif;"></h4>
        <p style="color: #e8e8e8; font-size: 13px; margin: 0; line-height: 1.4;"></p>
    </div>'''

new_label = '''    <div id="product-label" style="position: absolute; display: none; background: rgba(15,15,15,0.92); padding: 16px 24px; border-radius: 12px; pointer-events: none; transition: opacity 0.3s ease, transform 0.3s ease; z-index: 9999; border: 2px solid #C87533; backdrop-filter: blur(12px); max-width: 320px; box-shadow: 0 8px 32px rgba(200,117,51,0.15), 0 2px 8px rgba(0,0,0,0.4); transform: translateX(-50%);">
        <h4 style="color: #C87533; font-weight: 700; margin: 0 0 6px 0; font-size: 15px; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: 0.02em;"></h4>
        <p style="color: #d0d0d0; font-size: 12px; margin: 0; line-height: 1.5; font-family: 'Inter', sans-serif;"></p>
    </div>'''

if old_label in content:
    content = content.replace(old_label, new_label)
    replacements += 1
    print("✅ 4. Enhanced hover label with shadow + transform")
else:
    print("❌ 4. Could not find label block")

# ============================================================
# 5. Enable tone mapping
# ============================================================

old_renderer = '''            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setClearColor(0x000000, 0);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;'''

new_renderer = '''            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setClearColor(0x000000, 0);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            renderer.outputColorSpace = THREE.SRGBColorSpace;'''

if old_renderer in content:
    content = content.replace(old_renderer, new_renderer)
    replacements += 1
    print("✅ 5. Added ACES tone mapping + sRGB")
else:
    print("❌ 5. Could not find renderer block")

with open('index.html', 'w') as f:
    f.write(content)

print(f"\n{'='*50}")
print(f"Total replacements: {replacements}/5")
if replacements == 5:
    print("🎉 All patches applied successfully!")
else:
    print(f"⚠️  {5 - replacements} patches failed — check output above")
