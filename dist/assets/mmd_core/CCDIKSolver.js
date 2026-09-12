(function (global) {
    'use strict';

    const THREE = global.THREE;

    const _q = new THREE.Quaternion();
    const _targetPos = new THREE.Vector3();
    const _targetVec = new THREE.Vector3();
    const _effectorPos = new THREE.Vector3();
    const _effectorVec = new THREE.Vector3();
    const _linkPos = new THREE.Vector3();
    const _invLinkQ = new THREE.Quaternion();
    const _linkScale = new THREE.Vector3();
    const _axis = new THREE.Vector3();
    const _vector = new THREE.Vector3();
    const _matrix = new THREE.Matrix4();

    class CCDIKSolver {
        constructor(mesh, iks = []) {
            this.mesh = mesh;
            this.iks = iks;

            this._initialQuaternions = [];
            this._workingQuaternion = new THREE.Quaternion();

            for (const ik of iks) {
                const chainQuats = [];
                for (let i = 0; i < ik.links.length; i++) {
                    chainQuats.push(new THREE.Quaternion());
                }
                this._initialQuaternions.push(chainQuats);
            }

            this._valid();
        }

        update(globalBlendFactor = 1.0) {
            const iks = this.iks;

            for (let i = 0, il = iks.length; i < il; i++) {
                this.updateOne(iks[i], globalBlendFactor);
            }

            return this;
        }

        updateOne(ik, overrideBlend = 1.0) {
            const chainBlend = ik.blendFactor !== undefined ? ik.blendFactor : overrideBlend;
            const bones = this.mesh.skeleton.bones;
            const chainIndex = this.iks.indexOf(ik);
            const initialQuaternions = this._initialQuaternions[chainIndex];

            const math = Math;

            const effector = bones[ik.effector];
            const target = bones[ik.target];

            _targetPos.setFromMatrixPosition(target.matrixWorld);

            const links = ik.links;
            const iteration = ik.iteration !== undefined ? ik.iteration : 1;

            if (chainBlend < 1.0) {
                for (let j = 0; j < links.length; j++) {
                    const linkIndex = links[j].index;
                    initialQuaternions[j].copy(bones[linkIndex].quaternion);
                }
            }

            for (let i = 0; i < iteration; i++) {
                let rotated = false;

                for (let j = 0, jl = links.length; j < jl; j++) {
                    const link = bones[links[j].index];

                    if (links[j].enabled === false) break;

                    const limitation = links[j].limitation;
                    const rotationMin = links[j].rotationMin;
                    const rotationMax = links[j].rotationMax;

                    link.matrixWorld.decompose(_linkPos, _invLinkQ, _linkScale);
                    _invLinkQ.invert();
                    _effectorPos.setFromMatrixPosition(effector.matrixWorld);

                    _effectorVec.subVectors(_effectorPos, _linkPos);
                    _effectorVec.applyQuaternion(_invLinkQ);
                    _effectorVec.normalize();

                    _targetVec.subVectors(_targetPos, _linkPos);
                    _targetVec.applyQuaternion(_invLinkQ);
                    _targetVec.normalize();

                    let angle = _targetVec.dot(_effectorVec);

                    if (angle > 1.0) {
                        angle = 1.0;
                    } else if (angle < -1.0) {
                        angle = -1.0;
                    }

                    angle = math.acos(angle);

                    if (angle < 1e-5) continue;

                    if (ik.minAngle !== undefined && angle < ik.minAngle) {
                        angle = ik.minAngle;
                    }

                    if (ik.maxAngle !== undefined && angle > ik.maxAngle) {
                        angle = ik.maxAngle;
                    }

                    _axis.crossVectors(_effectorVec, _targetVec);
                    _axis.normalize();

                    _q.setFromAxisAngle(_axis, angle);
                    link.quaternion.multiply(_q);

                    if (limitation !== undefined) {
                        let c = link.quaternion.w;

                        if (c > 1.0) c = 1.0;

                        const c2 = math.sqrt(1 - c * c);
                        link.quaternion.set(limitation.x * c2, limitation.y * c2, limitation.z * c2, c);
                    }

                        if (rotationMin !== undefined) {
                            const euler = new THREE.Euler().setFromQuaternion(link.quaternion);
                            _vector.set(euler.x, euler.y, euler.z).max(rotationMin);
                            link.quaternion.setFromEuler(new THREE.Euler(_vector.x, _vector.y, _vector.z));
                        }

                        if (rotationMax !== undefined) {
                            const euler = new THREE.Euler().setFromQuaternion(link.quaternion);
                            _vector.set(euler.x, euler.y, euler.z).min(rotationMax);
                            link.quaternion.setFromEuler(new THREE.Euler(_vector.x, _vector.y, _vector.z));
                        }

                    link.updateMatrixWorld(true);
                    rotated = true;
                }

                if (!rotated) break;
            }

            if (chainBlend < 1.0) {
                for (let j = 0; j < links.length; j++) {
                    const linkIndex = links[j].index;
                    const link = bones[linkIndex];

                    this._workingQuaternion.copy(initialQuaternions[j]).slerp(link.quaternion, chainBlend);

                    link.quaternion.copy(this._workingQuaternion);
                    link.updateMatrixWorld(true);
                }
            }

            return this;
        }

        createHelper(sphereSize) {
            return new CCDIKHelper(this.mesh, this.iks, sphereSize);
        }

        _valid() {
            const iks = this.iks;
            const bones = this.mesh.skeleton.bones;

            for (let i = 0, il = iks.length; i < il; i++) {
                const ik = iks[i];
                const effector = bones[ik.effector];
                const links = ik.links;
                let link0, link1;

                link0 = effector;

                for (let j = 0, jl = links.length; j < jl; j++) {
                    link1 = bones[links[j].index];

                    if (link0.parent !== link1) {
                        console.warn('THREE.CCDIKSolver: bone ' + link0.name + ' is not the child of bone ' + link1.name);
                    }

                    link0 = link1;
                }
            }
        }
    }

    class CCDIKHelper extends THREE.Object3D {
        constructor(mesh, iks = [], sphereSize = 0.25) {
            super();

            this.root = mesh;
            this.iks = iks;

            this.matrix.copy(mesh.matrixWorld);
            this.matrixAutoUpdate = false;

            this.sphereGeometry = new THREE.SphereGeometry(sphereSize, 16, 8);

            this.targetSphereMaterial = new THREE.MeshBasicMaterial({
                color: new THREE.Color(0xff8888),
                depthTest: false,
                depthWrite: false,
                transparent: true
            });

            this.effectorSphereMaterial = new THREE.MeshBasicMaterial({
                color: new THREE.Color(0x88ff88),
                depthTest: false,
                depthWrite: false,
                transparent: true
            });

            this.linkSphereMaterial = new THREE.MeshBasicMaterial({
                color: new THREE.Color(0x8888ff),
                depthTest: false,
                depthWrite: false,
                transparent: true
            });

            this.lineMaterial = new THREE.LineBasicMaterial({
                color: new THREE.Color(0xff0000),
                depthTest: false,
                depthWrite: false,
                transparent: true
            });

            this._init();
        }

        updateMatrixWorld(force) {
            const mesh = this.root;

            if (this.visible) {
                let offset = 0;

                const iks = this.iks;
                const bones = mesh.skeleton.bones;

                _matrix.copy(mesh.matrixWorld).invert();

                for (let i = 0, il = iks.length; i < il; i++) {
                    const ik = iks[i];

                    const targetBone = bones[ik.target];
                    const effectorBone = bones[ik.effector];

                    const targetMesh = this.children[offset++];
                    const effectorMesh = this.children[offset++];

                    targetMesh.position.copy(getPosition(targetBone, _matrix));
                    effectorMesh.position.copy(getPosition(effectorBone, _matrix));

                    for (let j = 0, jl = ik.links.length; j < jl; j++) {
                        const link = ik.links[j];
                        const linkBone = bones[link.index];

                        const linkMesh = this.children[offset++];

                        linkMesh.position.copy(getPosition(linkBone, _matrix));
                    }

                    const line = this.children[offset++];
                    const array = line.geometry.attributes.position.array;

                    setPositionOfBoneToAttributeArray(array, 0, targetBone, _matrix);
                    setPositionOfBoneToAttributeArray(array, 1, effectorBone, _matrix);

                    for (let j = 0, jl = ik.links.length; j < jl; j++) {
                        const link = ik.links[j];
                        const linkBone = bones[link.index];
                        setPositionOfBoneToAttributeArray(array, j + 2, linkBone, _matrix);
                    }

                    line.geometry.attributes.position.needsUpdate = true;
                }
            }

            this.matrix.copy(mesh.matrixWorld);

            super.updateMatrixWorld(force);
        }

        dispose() {
            this.sphereGeometry.dispose();

            this.targetSphereMaterial.dispose();
            this.effectorSphereMaterial.dispose();
            this.linkSphereMaterial.dispose();
            this.lineMaterial.dispose();

            const children = this.children;

            for (let i = 0; i < children.length; i++) {
                const child = children[i];

                if (child.isLine) child.geometry.dispose();
            }
        }

        _init() {
            const scope = this;
            const iks = this.iks;

            function createLineGeometry(ik) {
                const geometry = new THREE.BufferGeometry();
                const vertices = new Float32Array((2 + ik.links.length) * 3);
                geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

                return geometry;
            }

            function createTargetMesh() {
                return new THREE.Mesh(scope.sphereGeometry, scope.targetSphereMaterial);
            }

            function createEffectorMesh() {
                return new THREE.Mesh(scope.sphereGeometry, scope.effectorSphereMaterial);
            }

            function createLinkMesh() {
                return new THREE.Mesh(scope.sphereGeometry, scope.linkSphereMaterial);
            }

            function createLine(ik) {
                return new THREE.Line(createLineGeometry(ik), scope.lineMaterial);
            }

            for (let i = 0, il = iks.length; i < il; i++) {
                const ik = iks[i];

                this.add(createTargetMesh());
                this.add(createEffectorMesh());

                for (let j = 0, jl = ik.links.length; j < jl; j++) {
                    this.add(createLinkMesh());
                }

                this.add(createLine(ik));
            }
        }
    }

    function getPosition(bone, matrixWorldInv) {
        return _vector
            .setFromMatrixPosition(bone.matrixWorld)
            .applyMatrix4(matrixWorldInv);
    }

    function setPositionOfBoneToAttributeArray(array, index, bone, matrixWorldInv) {
        const v = getPosition(bone, matrixWorldInv);

        array[index * 3 + 0] = v.x;
        array[index * 3 + 1] = v.y;
        array[index * 3 + 2] = v.z;
    }

    // 挂载到 THREE 上
    THREE.CCDIKSolver = CCDIKSolver;
    THREE.CCDIKHelper = CCDIKHelper;

})(typeof window !== 'undefined' ? window : this);