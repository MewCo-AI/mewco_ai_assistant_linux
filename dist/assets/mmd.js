const mmdPath = 'assets/mmd_model/小月/小月.pmx'; // 人物模型路径
const mouthMorphIndex = 133; // 嘴的 morph target 索引
const blinkMorphIndex = 60; // 眨眼的 morph target 索引

let camera, scene, renderer, controls, model, helper;
let mouthOpen = false;
let lastTime = Date.now();
let breathFactor = 0; // 呼吸动画的强度因子
let breathDirection = 1; // 呼吸动画的方向控制
let blinkInterval = 3000; // 眨眼间隔（毫秒）
let lastBlinkTime = Date.now(); // 上次眨眼的时间
let isBlinking = false; // 当前是否正在眨眼
let mouthYValue = 0; // 用于存储API返回的mouth_y值
init();
animate();
function init() {
    // 创建场景
    scene = new THREE.Scene();
    // 加载背景纹理
    const textureLoader = new THREE.TextureLoader();
    const bgTexture = textureLoader.load('/assets/image/bg.jpg');
    scene.background = bgTexture;
    // 创建相机
    camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 2000);
    camera.position.set(0, 10, 50);
    // 创建渲染器
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    // 创建控制器
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    // 添加环境光
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    // 添加平行光
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(1, 1, 1).normalize();
    scene.add(directionalLight);
    // 加载MMD模型
    const loader = new THREE.MMDLoader();
    loader.load(mmdPath,
        function (mmd) {
            model = mmd;
            scene.add(model);
            helper = new THREE.MMDAnimationHelper();
            helper.add(model, {
                physics: true // 启用物理效果
            });
        },
        function (xhr) {
            console.log((xhr.loaded / xhr.total * 100) + '% loaded');
        },
        function (error) {
            console.error('加载模型时出错', error);
        }
    );
    // 每隔100毫秒读取API
    setInterval(() => {
        fetch('/api/get_mouth_y')
            .then(response => response.json())
            .then(data => {
                mouthYValue = parseFloat(data.y);
            })
            .catch(error => {
                console.error('Error fetching mouth_y:', error);
            });
    }, 100);
}
function animate() {
    requestAnimationFrame(animate);
    if (helper) {
        helper.update(0.005); // 更新动画，参数为时间增量（秒）
        // 呼吸动画逻辑
        if (model && model.skeleton && model.skeleton.bones.length > 0) {
            const chestBone = findBoneByName(model.skeleton.bones, '上半身'); // 胸部骨骼名称为“上半身”
            if (chestBone) {
                breathFactor += breathDirection * 0.00001; // 控制呼吸的速度和幅度
                if (breathFactor >= 0.001 || breathFactor <= -0.001) {
                    breathDirection *= -1; // 反转方向
                }
                chestBone.position.y += breathFactor; // 上下移动骨骼
            }
            // 找到左右手的手臂骨骼并调整其旋转
            const leftUpperArmBone = findBoneByName(model.skeleton.bones, '左腕'); // 左手骨骼名称
            const rightUpperArmBone = findBoneByName(model.skeleton.bones, '右腕'); // 右手骨骼名称
            if (leftUpperArmBone && rightUpperArmBone) {
                // 设置左手旋转（高举）
                leftUpperArmBone.rotation.y = Math.PI / -3.5;
                leftUpperArmBone.rotation.z = Math.PI / -5;
                // 设置右手旋转（高举）
                rightUpperArmBone.rotation.y = Math.PI / 3.5;
                rightUpperArmBone.rotation.z = Math.PI / 5;
            }
        }
        // 动态控制嘴巴开合
        if (mouthYValue > 0.1) {
            const currentTime = Date.now();
            if (currentTime - lastTime >= 150) {
                mouthOpen = !mouthOpen;
                if (model.morphTargetInfluences) {
                    model.morphTargetInfluences[mouthMorphIndex] = mouthOpen ? 1 : 0;
                }
                lastTime = currentTime;
                // 小幅度随机运动
                applyRandomBodyMotion();
            }
        } else {
            // 当 mouthYValue <= 0.1 时，嘴巴闭合
            if (model.morphTargetInfluences) {
                model.morphTargetInfluences[mouthMorphIndex] = 0; // 闭合嘴巴
            }
        }
        // 眨眼逻辑
        if (model && model.morphTargetInfluences) {
            const now = Date.now();
            if (now - lastBlinkTime >= blinkInterval) {
                isBlinking = true;
                model.morphTargetInfluences[blinkMorphIndex] = 1; // 开始眨眼
                setTimeout(() => {
                    model.morphTargetInfluences[blinkMorphIndex] = 0; // 结束眨眼
                    isBlinking = false;
                    lastBlinkTime = now;
                }, 100); // 眨眼持续时间（毫秒）
            }
        }
    }
    controls.update();
    renderer.render(scene, camera);
}
// 根据名称查找骨骼
function findBoneByName(bones, name) {
    for (let bone of bones) {
        if (bone.name === name) {
            return bone;
        }
    }
    return null;
}
// 小幅度随机运动
function applyRandomBodyMotion() {
    if (model && model.skeleton && model.skeleton.bones.length > 0) {
        const headBone = findBoneByName(model.skeleton.bones, '頭'); // 头部骨骼名称为“頭”
        const leftShoulderBone = findBoneByName(model.skeleton.bones, '左肩'); // 左肩骨骼名称
        const rightShoulderBone = findBoneByName(model.skeleton.bones, '右肩'); // 右肩骨骼名称
        if (headBone) {
            headBone.rotation.x += (Math.random() - 0.5) * 0.02; // 随机上下倾斜
            headBone.rotation.y += (Math.random() - 0.5) * 0.02; // 随机左右转动
        }
        if (leftShoulderBone) {
            leftShoulderBone.rotation.x += (Math.random() - 0.5) * 0.02; // 随机上下倾斜
            leftShoulderBone.rotation.z += (Math.random() - 0.5) * 0.02; // 随机前后摆动
        }
        if (rightShoulderBone) {
            rightShoulderBone.rotation.x += (Math.random() - 0.5) * 0.02; // 随机上下倾斜
            rightShoulderBone.rotation.z += (Math.random() - 0.5) * 0.02; // 随机前后摆动
        }
    }
}
// 窗口大小变化时调整相机和渲染器
window.addEventListener('resize', function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});