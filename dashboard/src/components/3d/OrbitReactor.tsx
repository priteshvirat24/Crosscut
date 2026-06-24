"use client";

import { useRef, useMemo, useEffect } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Sphere, Line, Html } from "@react-three/drei";
import * as THREE from "three";

const TOTAL_TESTS = 418;
const TARGET_TESTS = 12;

const REPOSITORIES = [
  { id: "repo-1", name: "checkout", pos: new THREE.Vector3(-4, 3, -2) },
  { id: "repo-2", name: "analytics", pos: new THREE.Vector3(4, 2, -3) },
  { id: "repo-3", name: "refund", pos: new THREE.Vector3(-3, -3, 2) },
  { id: "repo-4", name: "billing", pos: new THREE.Vector3(3, -4, 1) }
];

function CameraController({ scene }: { scene: number }) {
  const { camera } = useThree();
  const targetPos = useRef(new THREE.Vector3(0, 0, 25));

  useEffect(() => {
    if (scene === 0) {
      targetPos.current.set(0, 0, 18);
    } else if (scene === 1) {
      targetPos.current.set(0, 2, 16);
    } else if (scene === 2 || scene === 3) {
      targetPos.current.set(3, 2, 22);
    } else if (scene === 4) {
      targetPos.current.set(-2, 1, 20);
    } else if (scene === 5) {
      targetPos.current.set(2, -1, 22);
    } else if (scene === 6) {
      targetPos.current.set(0, 0, 24);
    } else {
      targetPos.current.set(0, 0, 28);
    }
  }, [scene]);

  useFrame(() => {
    camera.position.lerp(targetPos.current, 0.015);
    camera.lookAt(0, 0, 0);
  });

  return null;
}

function DependencyGraph({ currentStage }: { currentStage: number }) {
  const groupRef = useRef<THREE.Group>(null);

  const testNodes = useMemo(() => {
    const arr = [];
    for (let i = 0; i < TOTAL_TESTS; i++) {
      const isTarget = i < TARGET_TESTS;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 8 + Math.random() * 6;
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta);
      const z = r * Math.cos(phi);
      const parentRepo = isTarget ? REPOSITORIES[i % REPOSITORIES.length] : null;
      arr.push({ id: i, pos: new THREE.Vector3(x, y, z), isTarget, parentRepo });
    }
    return arr;
  }, []);

  const testRefs = useRef<(THREE.Mesh | null)[]>([]);
  const centerNodeRef = useRef<THREE.Mesh>(null);
  const repoRefs = useRef<(THREE.Mesh | null)[]>([]);

  // Shared geometry and materials for massive performance boost
  const testGeo = useMemo(() => new THREE.SphereGeometry(0.15, 8, 8), []);
  const targetMat = useMemo(() => new THREE.MeshStandardMaterial({ color: "#E5484D", roughness: 0.2, metalness: 0.8 }), []);
  const ambientMat = useMemo(() => new THREE.MeshStandardMaterial({ color: "#8B8D86", roughness: 0.2, metalness: 0.8, transparent: true, opacity: 0.3 }), []);

  // Pre-allocate vector to prevent insane Garbage Collection stutter (50k objects/sec)
  const targetScaleVec = useMemo(() => new THREE.Vector3(), []);

  useFrame((state, delta) => {
    if (!groupRef.current) return;

    const baseSpeed = 0.06;
    groupRef.current.rotation.y += delta * baseSpeed;
    groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.15) * 0.08;

    if (centerNodeRef.current) {
      const breath = 1 + Math.sin(state.clock.elapsedTime * 1.5) * 0.04;
      targetScaleVec.set(breath, breath, breath);
      centerNodeRef.current.scale.lerp(targetScaleVec, 0.05);
    }

    REPOSITORIES.forEach((_, i) => {
      const mesh = repoRefs.current[i];
      if (mesh) {
        const breath = 1 + Math.sin(state.clock.elapsedTime * 1.2 + i) * 0.03;
        targetScaleVec.set(breath, breath, breath);
        mesh.scale.lerp(targetScaleVec, 0.05);
      }
    });

    testNodes.forEach((node, i) => {
      const mesh = testRefs.current[i];
      if (!mesh) return;

      if (currentStage >= 4 && currentStage < 6) {
        if (node.isTarget) {
          targetScaleVec.set(1.8, 1.8, 1.8);
          mesh.scale.lerp(targetScaleVec, 0.03);
        } else {
          targetScaleVec.set(0.001, 0.001, 0.001); // 0.001 prevents degenerate matrix vibration
          mesh.scale.lerp(targetScaleVec, 0.02 + (i % 20) * 0.001);
        }
      } else if (currentStage >= 6) {
        if (node.isTarget) {
          const pulse = 1.5 + Math.sin(state.clock.elapsedTime * 2 + i) * 0.15;
          targetScaleVec.set(pulse, pulse, pulse);
          mesh.scale.lerp(targetScaleVec, 0.05);
        } else {
          targetScaleVec.set(0.001, 0.001, 0.001);
          mesh.scale.lerp(targetScaleVec, 0.1);
        }
      } else {
        const breath = 1 + Math.sin(state.clock.elapsedTime * 0.8 + i * 0.3) * 0.05;
        targetScaleVec.set(breath, breath, breath);
        mesh.scale.lerp(targetScaleVec, 0.03);
      }
    });
  });

  return (
    <group ref={groupRef}>

      {/* CENTER NODE */}
      <Sphere ref={centerNodeRef} args={[0.5, 32, 32]} position={[0, 0, 0]}>
        <meshStandardMaterial color="#1E1E1E" roughness={0.2} metalness={0.8} />
        <Html distanceFactor={25} center position={[0, 0.8, 0]}>
          <div className="bg-transparent px-2 py-0.5 whitespace-nowrap pointer-events-none opacity-100">
            <span className="text-[10px] font-mono font-bold text-[#1E1E1E] drop-shadow-md">validate_payment()</span>
          </div>
        </Html>
      </Sphere>

      {/* REPOSITORY TRAVERSAL PATHS — always visible and prominent */}
      {REPOSITORIES.map((repo) => (
        <Line
          key={`repo-line-${repo.id}`}
          points={[new THREE.Vector3(0, 0, 0), repo.pos]}
          color="#C68A3A"
          lineWidth={2}
          transparent
          opacity={0.9}
        />
      ))}

      {/* REPOSITORY NODES */}
      {REPOSITORIES.map((repo, i) => (
        <Sphere key={repo.id} ref={(el) => { repoRefs.current[i] = el; }} args={[0.3, 32, 32]} position={repo.pos}>
          <meshStandardMaterial color="#C68A3A" roughness={0.2} metalness={0.8} />
          <Html distanceFactor={25} center position={[0, -0.6, 0]}>
            <div className="bg-transparent px-1.5 py-0.5 whitespace-nowrap pointer-events-none">
              <span className="text-[10px] font-bold uppercase tracking-widest text-[#C68A3A] drop-shadow-md">{repo.name}</span>
            </div>
          </Html>
        </Sphere>
      ))}

      {/* TEST CLOUD PATHS — always visible */}
      {testNodes.filter(n => n.isTarget).map((node) => (
        <Line
          key={`target-path-${node.id}`}
          points={[node.parentRepo!.pos, node.pos]}
          color="#E5484D"
          lineWidth={1}
          transparent
          opacity={0.7}
        />
      ))}

      {/* TEST CLOUD NODES */}
      {testNodes.map((node, i) => (
        <mesh
          key={node.id}
          ref={(el) => { testRefs.current[i] = el; }}
          position={node.pos}
          geometry={testGeo}
          material={node.isTarget ? targetMat : ambientMat}
        />
      ))}

    </group>
  );
}

export function OrbitReactor({ currentStage = -1 }: { currentStage?: number }) {
  return (
    <div className="w-full h-full bg-transparent relative overflow-hidden flex items-center justify-center">
      <Canvas 
        camera={{ position: [0, 0, 25], fov: 45 }}
        dpr={[1, 1.5]}
        performance={{ min: 0.5 }}
      >
        <ambientLight intensity={1.5} />
        <directionalLight position={[10, 10, 5]} intensity={2} color="#ffffff" />
        <directionalLight position={[-10, -10, -5]} intensity={1} color="#FAFAF8" />
        <pointLight position={[0, 0, 0]} intensity={1} color="#C68A3A" />

        <CameraController scene={currentStage} />
        <DependencyGraph currentStage={currentStage} />

        <OrbitControls
          enableZoom={true}
          enablePan={true}
          autoRotate={false}
          enableDamping={true}
          dampingFactor={0.05}
        />
      </Canvas>
    </div>
  );
}
