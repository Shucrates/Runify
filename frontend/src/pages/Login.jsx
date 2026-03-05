import React from 'react';
import { PlayCircle } from 'lucide-react';

const Login = () => {
    const handleStravaLogin = () => {
        window.location.href = 'http://localhost:8000/auth/strava/login';
    };

    return (
        <div className="min-h-screen bg-zinc-950 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">

                {/* Decorative gradient blur */}
                <div className="absolute top-[-50px] right-[-50px] w-32 h-32 bg-orange-500 rounded-full blur-[80px] opacity-30"></div>
                <div className="absolute bottom-[-50px] left-[-50px] w-32 h-32 bg-green-500 rounded-full blur-[80px] opacity-20"></div>

                <div className="flex flex-col items-center mb-10 relative z-10">
                    <div className="bg-gradient-to-tr from-orange-500 to-amber-500 p-3 rounded-full mb-4 shadow-lg shadow-orange-500/20">
                        <PlayCircle size={32} className="text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Runify</h1>
                    <p className="text-zinc-400 mt-2 text-center text-sm">
                        Sync your Strava efforts with your Spotify rhythm
                    </p>
                </div>

                <div className="space-y-4 relative z-10">
                    <button
                        onClick={handleStravaLogin}
                        className="w-full bg-[#FC4C02] hover:bg-[#E34402] text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg shadow-orange-500/20 active:scale-[0.98]"
                    >
                        <span>Connect with Strava</span>
                    </button>
                </div>

                <p className="text-xs text-zinc-600 text-center mt-8">
                    By continuing, you agree to let Runify read your Strava and Spotify history.
                </p>
            </div>
        </div>
    );
};

export default Login;
