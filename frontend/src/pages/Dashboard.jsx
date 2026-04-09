import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { RefreshCw, Activity, Music, TrendingUp, Flame, Heart, Clock, Mountain, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import { format } from 'date-fns';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const Dashboard = () => {
    const [searchParams] = useSearchParams();
    const userId = searchParams.get('user_id');
    const spotifyConnected = searchParams.get('spotify_connected') === 'true';

    const [runs, setRuns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [syncing, setSyncing] = useState(false);
    const [aiStates, setAiStates] = useState({});
    const [sortBy, setSortBy] = useState('latest');

    useEffect(() => {
        if (userId && spotifyConnected) {
            fetchRuns();
        } else {
            setLoading(false);
        }
    }, [userId, spotifyConnected]);

    const fetchRuns = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/runs/?user_id=${userId}`);
            setRuns(response.data);
        } catch (error) {
            console.error("Error fetching runs:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSync = async () => {
        setSyncing(true);
        try {
            await axios.post(`http://localhost:8000/runs/sync?user_id=${userId}`);
            await fetchRuns();
        } catch (error) {
            alert("Error syncing data: " + (error.response?.data?.detail || error.message));
        } finally {
            setSyncing(false);
        }
    };

    const handleGenerateAI = async (run) => {
        const id = run.id;
        if (aiStates[id]?.summary) {
            setAiStates(prev => ({ ...prev, [id]: { ...prev[id], open: !prev[id].open } }));
            return;
        }
        setAiStates(prev => ({ ...prev, [id]: { loading: true, summary: null, open: true } }));
        try {
            const res = await axios.post(`http://localhost:8000/ai/summary?run_id=${id}&user_id=${userId}`);
            setAiStates(prev => ({ ...prev, [id]: { loading: false, summary: res.data.summary, open: true } }));
        } catch (err) {
            setAiStates(prev => ({
                ...prev,
                [id]: { loading: false, summary: '⚠️ Failed to generate report. Please try again.', open: true }
            }));
        }
    };

    const handleSpotifyLogin = () => {
        window.location.href = `http://localhost:8000/auth/spotify/login?user_id=${userId}`;
    };

    // Calculate aggregated stats
    const totalDistance = runs.reduce((acc, r) => acc + r.distance_meters, 0) / 1000;
    const totalRuns = runs.length;
    const totalTimeSecs = runs.reduce((acc, r) => acc + r.elapsed_time_seconds, 0);
    const avgPaceSecs = totalDistance > 0 ? totalTimeSecs / totalDistance : 0;
    
    const formatPace = (secs) => {
        if (!secs) return '--:--';
        const m = Math.floor(secs / 60);
        const s = Math.floor(secs % 60);
        return `${m}:${s.toString().padStart(2, '0')}/km`;
    };

    const formatTimeHms = (totalSecs) => {
        const h = Math.floor(totalSecs / 3600);
        const m = Math.floor((totalSecs % 3600) / 60);
        return h > 0 ? `${h}h ${m}m` : `${m}m`;
    };

    const sortedRuns = [...runs].sort((a, b) => {
        if (sortBy === 'distance') return b.distance_meters - a.distance_meters;
        if (sortBy === 'pace') {
            const paceA = a.distance_meters > 0 ? a.elapsed_time_seconds / (a.distance_meters/1000) : 9999;
            const paceB = b.distance_meters > 0 ? b.elapsed_time_seconds / (b.distance_meters/1000) : 9999;
            return paceA - paceB; // lower pace is better (faster)
        }
        return new Date(b.start_date) - new Date(a.start_date);
    });

    if (!userId) {
        return <div className="min-h-screen bg-black text-white flex items-center justify-center">Please login from home page.</div>;
    }

    return (
        <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans pb-20">
            {/* Minimal Header area */}
            <div className="max-w-4xl mx-auto pt-10 px-6 mb-10 flex justify-between items-start">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-[#0ba523] rounded-full flex items-center justify-center shadow-[0_0_15px_rgba(11,165,35,0.3)]">
                        <Activity size={24} className="text-black" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white tracking-tight">Your Runs</h1>
                        <p className="text-zinc-500 text-sm mt-1">Track your progress and favorite songs</p>
                    </div>
                </div>
                {spotifyConnected && (
                    <button 
                        onClick={handleSync} 
                        disabled={syncing}
                        className="flex items-center gap-2 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg hover:bg-zinc-800 transition text-sm text-zinc-300"
                    >
                        <RefreshCw size={14} className={syncing ? "animate-spin text-green-500" : ""} />
                        <span>Sync</span>
                    </button>
                )}
            </div>

            <main className="max-w-4xl mx-auto px-6">
                {!spotifyConnected ? (
                    <div className="bg-[#111] border border-zinc-900 rounded-xl p-10 text-center">
                        <button onClick={handleSpotifyLogin} className="bg-[#1DB954] text-black px-6 py-3 rounded-full font-bold">Connect Spotify</button>
                    </div>
                ) : loading ? (
                    <div className="flex justify-center p-20"><RefreshCw className="animate-spin text-zinc-500" /></div>
                ) : (
                    <>
                        {/* Highlights Grid */}
                        {runs.length > 0 && (
                            <div className="mb-12">
                                <h2 className="text-xl font-bold text-white mb-4">This Week's Stats</h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    <div className="bg-[#111111] rounded-xl p-5 border border-zinc-800/40">
                                        <div className="flex justify-between items-start mb-3">
                                            <span className="text-zinc-400 text-xs font-semibold uppercase tracking-wider">Total Distance</span>
                                            <TrendingUp size={16} className="text-[#0ba523]" />
                                        </div>
                                        <div className="text-2xl font-bold text-white">{totalDistance.toFixed(1)} <span className="text-sm font-normal text-zinc-500">km</span></div>
                                    </div>
                                    
                                    <div className="bg-[#111111] rounded-xl p-5 border border-zinc-800/40">
                                        <div className="flex justify-between items-start mb-3">
                                            <span className="text-zinc-400 text-xs font-semibold uppercase tracking-wider">Total Runs</span>
                                            <Activity size={16} className="text-blue-500" />
                                        </div>
                                        <div className="text-2xl font-bold text-white">{totalRuns} <span className="text-sm font-normal text-zinc-500">runs</span></div>
                                    </div>

                                    <div className="bg-[#111111] rounded-xl p-5 border border-zinc-800/40">
                                        <div className="flex justify-between items-start mb-3">
                                            <span className="text-zinc-400 text-xs font-semibold uppercase tracking-wider">Avg Pace</span>
                                            <TrendingUp size={16} className="text-[#0ba523]" />
                                        </div>
                                        <div className="text-2xl font-bold text-white">{formatPace(avgPaceSecs)}</div>
                                    </div>

                                    {/* Mocked/Calculated metrics showing zeros since Strava partial data doesn't have it yet */}
                                    <div className="bg-[#111111] rounded-xl p-5 border border-zinc-800/40">
                                        <div className="flex justify-between items-start mb-3">
                                            <span className="text-zinc-400 text-xs font-semibold uppercase tracking-wider">Calories Burned</span>
                                            <Flame size={16} className="text-orange-500" />
                                        </div>
                                        <div className="text-2xl font-bold text-white">-- <span className="text-sm font-normal text-zinc-500">kcal</span></div>
                                    </div>

                                    <div className="bg-[#111111] rounded-xl p-5 border border-zinc-800/40">
                                        <div className="flex justify-between items-start mb-3">
                                            <span className="text-zinc-400 text-xs font-semibold uppercase tracking-wider">Avg Heart Rate</span>
                                            <Heart size={16} className="text-red-500" />
                                        </div>
                                        <div className="text-2xl font-bold text-white">-- <span className="text-sm font-normal text-zinc-500">bpm</span></div>
                                    </div>

                                    <div className="bg-[#111111] rounded-xl p-5 border border-zinc-800/40">
                                        <div className="flex justify-between items-start mb-3">
                                            <span className="text-zinc-400 text-xs font-semibold uppercase tracking-wider">Total Time</span>
                                            <Activity size={16} className="text-purple-500" />
                                        </div>
                                        <div className="text-2xl font-bold text-white">{formatTimeHms(totalTimeSecs)}</div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Recent Runs List */}
                        <div>
                            <div className="flex justify-between items-end mb-6">
                                <h2 className="text-xl font-bold text-white">Recent Runs</h2>
                                <div className="flex gap-1 bg-[#111] p-1 border border-zinc-800/50 rounded-lg text-xs font-semibold">
                                    {['latest', 'distance', 'pace'].map((opt) => (
                                        <button 
                                            key={opt}
                                            onClick={() => setSortBy(opt)}
                                            className={`px-3 py-1.5 rounded-md capitalize ${sortBy === opt ? 'bg-[#0ba523] text-black shadow-sm' : 'text-zinc-400 hover:text-white'}`}
                                        >
                                            {opt}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4">
                                {sortedRuns.map((run) => {
                                    const distKm = (run.distance_meters / 1000).toFixed(2);
                                    const pace = formatPace(run.distance_meters > 0 ? (run.elapsed_time_seconds / (run.distance_meters/1000)) : 0);
                                    const timeHms = formatTimeHms(run.elapsed_time_seconds);
                                    const ai = aiStates[run.id] || {};

                                    return (
                                        <div key={run.id} className="bg-[#111111] border border-zinc-800/40 rounded-xl overflow-hidden hover:border-zinc-700/60 transition-colors">
                                            <div className="p-6">
                                                <div className="flex justify-between items-start mb-6">
                                                    <div>
                                                        <h3 className="text-lg font-bold text-white tracking-tight">{run.name}</h3>
                                                        <p className="text-xs text-zinc-500 mt-1">{format(new Date(run.start_date), 'EEE, MMM d • h:mm a')}</p>
                                                        {run.tracks.length > 0 && (
                                                            <div className="flex items-center gap-1 mt-3 text-xs text-zinc-400">
                                                                <Music size={12} className="text-purple-400" />
                                                                Listen to {run.tracks.length} tracks
                                                            </div>
                                                        )}
                                                    </div>
                                                    <div className="text-right">
                                                        <div className="text-2xl font-black text-[#0ba523]">{distKm} km</div>
                                                        <div className="text-sm font-medium text-zinc-400 mt-1">{timeHms}</div>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-zinc-800/50 text-left">
                                                    <div>
                                                        <div className="flex items-center gap-1 text-[10px] text-zinc-500 font-semibold uppercase mb-1">
                                                            Pace
                                                        </div>
                                                        <div className="text-sm font-bold text-white">{pace}</div>
                                                    </div>
                                                    <div>
                                                        <div className="flex items-center gap-1 text-[10px] text-zinc-500 font-semibold uppercase mb-1">
                                                            <Mountain size={10} className="text-[#0ba523]" /> Elevation
                                                        </div>
                                                        <div className="text-sm font-bold text-white">--m</div>
                                                    </div>
                                                    <div>
                                                        <div className="flex items-center gap-1 text-[10px] text-zinc-500 font-semibold uppercase mb-1">
                                                            Calories
                                                        </div>
                                                        <div className="text-sm font-bold text-white">--</div>
                                                    </div>
                                                    <div>
                                                        <div className="flex items-center gap-1 text-[10px] text-zinc-500 font-semibold uppercase mb-1">
                                                            <Heart size={10} className="text-red-500" /> HR Avg
                                                        </div>
                                                        <div className="text-sm font-bold text-white">-- bpm</div>
                                                    </div>
                                                </div>
                                                
                                                {/* Hidden tracks / AI UI beneath the main card details */}
                                                <div className="mt-8 pt-4 border-t border-zinc-800/50">
                                                    <div className="flex items-center justify-between">
                                                        <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-widest flex items-center gap-2">
                                                            <Music size={12} /> Soundtrack
                                                        </h4>
                                                        <button
                                                            onClick={() => handleGenerateAI(run)}
                                                            disabled={ai.loading}
                                                            className={`flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-md transition-all ${
                                                                ai.summary ? 'bg-purple-900/30 text-purple-400 hover:bg-purple-900/50' : 'bg-zinc-800 hover:bg-zinc-700 text-white'
                                                            }`}
                                                        >
                                                            {ai.loading ? <RefreshCw size={12} className="animate-spin" /> : <Sparkles size={12} className="text-purple-400" />}
                                                            {ai.summary ? (ai.open ? 'Hide Report' : 'Show Report') : 'AI Run Report'}
                                                        </button>
                                                    </div>
                                                    
                                                    {/* Tracks summary snippet */}
                                                    {run.tracks.length > 0 && !ai.open && (
                                                        <div className="flex gap-2 mt-3 overflow-x-auto pb-2 scrollbar-none">
                                                            {run.tracks.slice(0, 5).map((track, i) => (
                                                                <a key={i} href={track.external_url} target="_blank" rel="noreferrer" className="flex-shrink-0">
                                                                    <img src={track.album_image_url || 'https://via.placeholder.com/40'} alt="cover" className="w-10 h-10 rounded object-cover shadow-md border border-zinc-800" />
                                                                </a>
                                                            ))}
                                                            {run.tracks.length > 5 && (
                                                                <div className="w-10 h-10 rounded bg-zinc-800 flex items-center justify-center text-xs text-zinc-400 font-bold border border-zinc-700/50">
                                                                    +{run.tracks.length - 5}
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}

                                                    {/* AI Panel */}
                                                    {ai.open && ai.summary && (
                                                        <div className="mt-4 p-5 rounded-lg bg-zinc-900/80 border border-purple-900/30">
                                                            <div className="prose prose-invert prose-sm max-w-none 
                                                                prose-headings:text-purple-300 prose-headings:text-xs prose-headings:uppercase prose-headings:tracking-widest prose-headings:mt-4 prose-headings:mb-2
                                                                prose-p:text-zinc-300 prose-p:leading-relaxed text-sm">
                                                                <ReactMarkdown>{ai.summary}</ReactMarkdown>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>

                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
};

export default Dashboard;

