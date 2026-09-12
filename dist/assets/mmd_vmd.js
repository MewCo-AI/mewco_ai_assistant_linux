const mmdPath = 'assets/mmd_model/小月/小月.pmx'; // 人物模型路径
const vmdPath = 'assets/mmd_action/example.vmd'; // 人物动作路径

let camera, scene, renderer, controls, model, helper;
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
    loader.loadWithAnimation(mmdPath, vmdPath,
        function (mmd) {
            model = mmd.mesh;
            scene.add(model);
            // 创建动画助手
            helper = new THREE.MMDAnimationHelper();
            helper.add(model, {
                animation: mmd.animation,
                physics: true
            });
        },
        function (xhr) {
            console.log((xhr.loaded / xhr.total * 100) + '% 已加载');
        },
        function (error) {
            console.error('发生错误', error);
        }
    );
}
function animate() {
    requestAnimationFrame(animate);
    // 更新动画
    if (helper) {
        helper.update(0.005); // 使用时间差（秒）更新动画
    }
    // 更新控制器
    controls.update();
    // 渲染场景
    renderer.render(scene, camera);
}
// 窗口大小变化时调整相机和渲染器
window.addEventListener('resize', function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});