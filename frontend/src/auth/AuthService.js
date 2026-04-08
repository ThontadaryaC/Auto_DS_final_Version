import * as faceapi from 'face-api.js';

const USERS_KEY = 'autods_users';
const SESSION_KEY = 'autods_session';

export const AuthService = {
    // Load face-api models
    loadModels: async () => {
        const MODEL_URL = '/models';
        console.log('Starting model initialization from:', MODEL_URL);
        try {
            console.log('Loading TinyFaceDetector...');
            await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
            console.log('TinyFaceDetector Loaded.');

            console.log('Loading FaceLandmark68Net...');
            await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
            console.log('FaceLandmark68Net Loaded.');

            console.log('Loading FaceRecognitionNet...');
            await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);
            console.log('FaceRecognitionNet Loaded.');

            console.log('All models successfully initialized.');
        } catch (err) {
            console.error('Error in model loading:', err);
            throw err;
        }
    },

    // Get all users from localStorage
    getUsers: () => {
        const users = localStorage.getItem(USERS_KEY);
        return users ? JSON.parse(users) : [];
    },

    // Signup a new user
    signup: async (name, password, descriptor) => {
        const users = AuthService.getUsers();
        if (users.find(u => u.name.toLowerCase() === name.toLowerCase())) {
            throw new Error('User already exists');
        }
        
        // Convert descriptor (Float32Array) to array for JSON storage
        const newUser = {
            name,
            password,
            descriptor: Array.from(descriptor)
        };
        
        users.push(newUser);
        localStorage.setItem(USERS_KEY, JSON.stringify(users));
        AuthService.login(name);
    },

    // Login a user (manual)
    manualLogin: (name, password) => {
        const users = AuthService.getUsers();
        const user = users.find(u => u.name.toLowerCase() === name.toLowerCase() && u.password === password);
        if (user) {
            AuthService.login(name);
            return true;
        }
        return false;
    },

    // Check face match
    findUserByFace: (descriptor) => {
        const users = AuthService.getUsers();
        if (users.length === 0) return null;

        const labeledDescriptors = users.map(u => {
            return new faceapi.LabeledFaceDescriptors(u.name, [new Float32Array(u.descriptor)]);
        });

        const faceMatcher = new faceapi.FaceMatcher(labeledDescriptors, 0.6); // 0.6 threshold
        const bestMatch = faceMatcher.findBestMatch(descriptor);
        
        if (bestMatch.label !== 'unknown') {
            return bestMatch.label;
        }
        return null;
    },

    // Session Management (Using sessionStorage for higher security/frequent login)
    login: (name) => {
        sessionStorage.setItem(SESSION_KEY, JSON.stringify({ name, timestamp: Date.now() }));
    },

    logout: () => {
        sessionStorage.removeItem(SESSION_KEY);
        localStorage.removeItem(SESSION_KEY); // Clean up any old localStorage session too
    },

    isAuthenticated: () => {
        // Try sessionStorage first (active session)
        let session = sessionStorage.getItem(SESSION_KEY);
        
        // If not in sessionStorage, check legacy localStorage but migrate it or reject
        if (!session) {
            session = localStorage.getItem(SESSION_KEY);
            if (session) {
                // If we find an old session, let's treat it as expired for safety,
                // or just remove it to force login once.
                localStorage.removeItem(SESSION_KEY);
                return false;
            }
            return false;
        }
        
        try {
            const data = JSON.parse(session);
            if (!data || !data.name || !data.timestamp) {
                AuthService.logout();
                return false;
            }
            
            // Session valid for 24 hours
            if (Date.now() - data.timestamp > 24 * 60 * 60 * 1000) {
                AuthService.logout();
                return false;
            }
            return true;
        } catch (e) {
            AuthService.logout();
            return false;
        }
    },

    getCurrentUser: () => {
        const session = sessionStorage.getItem(SESSION_KEY);
        return session ? JSON.parse(session).name : null;
    }
};

