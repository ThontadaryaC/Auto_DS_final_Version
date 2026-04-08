import React, { useState, useEffect, useRef } from 'react';
import * as faceapi from 'face-api.js';
import { AuthService } from './AuthService';
import { Scan, User, Lock, ArrowRight, UserPlus, Fingerprint, RefreshCcw, CheckCircle2 } from 'lucide-react';

const LoginScreen = ({ onLogin }) => {
    const [mode, setMode] = useState('signin'); // 'signin' or 'signup'
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [name, setName] = useState('');
    const [password, setPassword] = useState('');
    const [scanning, setScanning] = useState(false);
    const [status, setStatus] = useState('Ready');
    const [progress, setProgress] = useState(0);

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [modelsLoaded, setModelsLoaded] = useState(false);
    const [cameraActive, setCameraActive] = useState(false);

    // Load Models on Mount
    useEffect(() => {
        const load = async () => {
            try {
                await AuthService.loadModels();
                setModelsLoaded(true);
                setLoading(false);
                
                // If no users exist, default to signup mode
                const existingUsers = AuthService.getUsers();
                if (existingUsers.length === 0) {
                    setMode('signup');
                }
            } catch (err) {
                setError('Failed to load face detection models.');
                setLoading(false);
            }
        };
        load();

        return () => {
            stopVideo();
        };
    }, []);

    // Start Video when models are loaded and UI is ready
    useEffect(() => {
        if (!loading && modelsLoaded) {
            // Small timeout to ensure DOM is fully painted
            const timer = setTimeout(() => {
                startVideo();
            }, 100);
            return () => clearTimeout(timer);
        }
    }, [loading, modelsLoaded]);

    const startVideo = () => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setError('Browser does not support camera access.');
            return;
        }

        setCameraActive(false);
        navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
            .then(stream => {
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    setCameraActive(true);
                    console.log('Camera started successfully');
                } else {
                    console.error('Video ref is null');
                    // Retry once if ref is null
                    setTimeout(startVideo, 200);
                }
            })
            .catch(err => {
                console.error('Camera error:', err);
                setCameraActive(false);
                setError('Camera access denied. Please enable camera permissions in your browser settings.');
            });
    };

    const stopVideo = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            videoRef.current.srcObject.getTracks().forEach(track => track.stop());
        }
    };

    const handleFaceAction = async () => {
        if (!modelsLoaded) {
            setError('Please wait, AI models are still initializing...');
            return;
        }
        if (!videoRef.current || !videoRef.current.srcObject) {
            setError('Camera connection lost. Please try reloading the camera feed.');
            return;
        }
        
        setError(null);
        setScanning(true);
        setStatus('Detecting Face...');
        setProgress(10);

        try {
            // Ensure video is ready
            if (videoRef.current.readyState < 2) {
                setStatus('Initializing stream sensor...');
                await new Promise(resolve => {
                    videoRef.current.onloadedmetadata = resolve;
                    // If it takes too long, resolve anyway to try
                    setTimeout(resolve, 1000);
                });
            }

            // Detect single face with landmarks and descriptor
            const detection = await faceapi.detectSingleFace(
                videoRef.current, 
                new faceapi.TinyFaceDetectorOptions()
            ).withFaceLandmarks().withFaceDescriptor();

            if (!detection) {
                setStatus('No face detected. Please align your face.');
                setScanning(false);
                return;
            }

            setProgress(60);
            
            if (mode === 'signup') {
                if (!name || !password) {
                    setError('Please enter name and password first.');
                    setScanning(false);
                    return;
                }
                setStatus('Registering biometric profile...');
                await AuthService.signup(name, password, detection.descriptor);
                stopVideo();
                setProgress(100);
                setTimeout(() => onLogin(name), 500);
            } else {
                setStatus('Verifying identity...');
                const matchedUser = AuthService.findUserByFace(detection.descriptor);
                
                if (matchedUser) {
                    setStatus(`Welcome back, ${matchedUser}!`);
                    stopVideo();
                    setProgress(100);
                    AuthService.login(matchedUser);
                    setTimeout(() => onLogin(matchedUser), 800);
                } else {
                    setError('Face not recognized. Please sign up or use password.');
                    setScanning(false);
                }
            }
        } catch (err) {
            setError(err.message || 'Verification failed.');
            setScanning(false);
        }
    };

    const handleManualLogin = (e) => {
        e.preventDefault();
        setError(null);
        if (AuthService.manualLogin(name, password)) {
            setStatus('Login successful');
            stopVideo();
            onLogin(name);
        } else {
            setError('Invalid name or password.');
        }
    };

    if (loading) {
        return (
            <div className="fixed inset-0 bg-slate-900 flex flex-col items-center justify-center z-[9999]">
                <RefreshCcw className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                <h2 className="text-xl font-bold text-white tracking-widest uppercase">System Initializing...</h2>
                <p className="text-blue-200/50 mt-2">Loading Biometric Modules</p>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 z-[9999] bg-slate-900 overflow-hidden flex items-center justify-center p-4">
            {/* Animated Background */}
            <div className="absolute inset-0 opacity-20">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-900/40 via-transparent to-transparent"></div>
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border border-blue-500/10 rounded-full animate-pulse-slow"></div>
            </div>

            <div className="relative w-full max-w-4xl flex flex-col md:flex-row bg-slate-800/40 backdrop-blur-2xl border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
                
                {/* Left Side: Video Preview */}
                <div className="w-full md:w-1/2 relative bg-black aspect-video md:aspect-auto">
                    <video 
                        ref={videoRef} 
                        autoPlay 
                        muted 
                        playsInline
                        className="w-full h-full object-cover grayscale-[20%] contrast-110"
                    />
                    
                    {/* Camera Retry Overlay */}
                    {!cameraActive && !loading && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/80 backdrop-blur-sm z-10 transition-opacity">
                            <button 
                                onClick={startVideo}
                                className="flex flex-col items-center gap-4 text-blue-400 hover:text-blue-300 transition-all p-8 rounded-2xl border border-blue-500/10 hover:bg-blue-500/5 group"
                            >
                                <RefreshCcw className="w-12 h-12 group-hover:rotate-180 transition-transform duration-700" />
                                <span className="text-xs font-mono uppercase tracking-[0.2em]">Initialize Optical Sensor</span>
                            </button>
                        </div>
                    )}
                    
                    {/* Scanning Animation */}
                    {scanning && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                            <div className="w-48 h-48 border-2 border-dashed border-blue-500/50 rounded-full animate-spin-slow"></div>
                            <div className="absolute top-0 left-0 w-full h-[2px] bg-blue-500/50 shadow-[0_0_15px_#3b82f6] animate-scanline"></div>
                        </div>
                    )}

                    {/* Overlay Decorations */}
                    <div className="absolute top-4 left-4 p-2 bg-blue-600/20 backdrop-blur-md rounded-lg border border-blue-500/30 flex items-center gap-2">
                        <Scan className="w-4 h-4 text-blue-400" />
                        <span className="text-xs font-mono text-blue-200 uppercase tracking-tighter">Biometric Scan Active</span>
                    </div>

                    <div className="absolute bottom-4 left-4 right-4 flex flex-col gap-2">
                        <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                            <div 
                                className="h-full bg-blue-500 transition-all duration-500 ease-out shadow-[0_0_10px_#3b82f6]" 
                                style={{ width: `${progress}%` }}
                            ></div>
                        </div>
                        <p className="text-[10px] font-mono text-white/50 uppercase tracking-widest text-center">{status}</p>
                    </div>
                </div>

                {/* Right Side: Form */}
                <div className="w-full md:w-1/2 p-8 flex flex-col justify-center gap-6">
                    <div className="text-center md:text-left">
                        <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
                            {mode === 'signin' ? 'Welcome Back' : 'Security Enrollment'}
                        </h1>
                        <p className="text-slate-400 text-sm">
                            {mode === 'signin' 
                                ? 'Verify your identity to access the terminal' 
                                : 'Register your biometric profile for secure access'}
                        </p>
                    </div>

                    {error && (
                        <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-3 rounded-xl text-xs flex items-center gap-2">
                            <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse"></div>
                            {error}
                        </div>
                    )}

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Terminal ID</label>
                            <div className="relative group">
                                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-500 transition-colors" />
                                <input 
                                    type="text" 
                                    placeholder="Enter identifier..."
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    className="w-full bg-slate-900/50 border border-white/5 focus:border-blue-500/50 outline-none rounded-xl py-3 pl-11 pr-4 text-white placeholder:text-slate-600 transition-all"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Access Key</label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-500 transition-colors" />
                                <input 
                                    type="password" 
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-slate-900/50 border border-white/5 focus:border-blue-500/50 outline-none rounded-xl py-3 pl-11 pr-4 text-white placeholder:text-slate-600 transition-all"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col gap-3 pt-2">
                        <button 
                            onClick={handleFaceAction}
                            disabled={scanning}
                            className={`w-full py-3.5 rounded-xl flex items-center justify-center gap-2 font-bold text-sm tracking-wide transition-all shadow-lg ${
                                scanning 
                                ? 'bg-slate-700 text-slate-500 cursor-not-allowed' 
                                : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/20'
                            }`}
                        >
                            {scanning ? <RefreshCcw className="w-4 h-4 animate-spin" /> : <Fingerprint className="w-4 h-4" />}
                            {mode === 'signin' ? 'Verify Biometrics' : 'Finalize Enrollment'}
                        </button>

                        <div className="flex items-center gap-2 py-2">
                            <div className="h-[1px] flex-1 bg-white/5"></div>
                            <span className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">OR</span>
                            <div className="h-[1px] flex-1 bg-white/5"></div>
                        </div>

                        <button 
                            onClick={handleManualLogin}
                            className="w-full py-3 bg-white/5 hover:bg-white/10 text-white rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2 border border-white/5"
                        >
                            Access with Key <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                    </div>

                    <div className="text-center pt-4">
                        <button 
                            onClick={() => {
                                setMode(mode === 'signin' ? 'signup' : 'signin');
                                setError(null);
                            }}
                            className="text-xs text-blue-400/60 hover:text-blue-400 font-medium transition-colors flex items-center justify-center gap-2 mx-auto"
                        >
                            {mode === 'signin' ? (
                                <>Need a new profile? <UserPlus className="w-3 h-3" /></>
                            ) : (
                                <>Existing profile? Sign in <ArrowRight className="w-3 h-3" /></>
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Custom Styles for Scanline and Pulse */}
            <style dangerouslySetInnerHTML={{ __html: `
                @keyframes scanline {
                    0% { transform: translateY(0); }
                    100% { transform: translateY(100vh); }
                }
                .animate-scanline {
                    animation: scanline 3s linear infinite;
                }
                @keyframes pulse-slow {
                    0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.1; }
                    50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.2; }
                }
                .animate-pulse-slow {
                    animation: pulse-slow 8s ease-in-out infinite;
                }
                .animate-spin-slow {
                    animation: spin 12s linear infinite;
                }
            `}} />
        </div>
    );
};

export default LoginScreen;
