import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { RefreshCw, Activity, Music, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import axios from 'axios';

const Dashboard = () => {
    const [searchParams] = useSearchParams();
    const userId = searchParams.get('user_id');
    const spotifyConnected = searchParams.get('spotify_connected') === 'true';

    const [runs, setRuns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [syncing, setSyncing] = useState(false);

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

    const handleSpotifyLogin = () => {
        window.location.href = `http://localhost:8000/auth/spotify/login?user_id=${userId}`;
    };

    const handleSync = async () => {
        setSyncing(true);
        try {
            await axios.post(`http://localhost:8000/runs/sync?user_id=${userId}`);
            await fetchRuns(); // Refetch data after sync
        } catch (error) {
            alert("Error syncing data: " + (error.response?.data?.detail || error.message));
        } finally {
            setSyncing(false);
        }
    };

    if (!userId) {
        return <div className="min-h-screen bg-zinc-950 flex justify-center items-center text-zinc-400">Please login from the home page.</div>;
    }

    return (
        <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6 md:p-10">
            <header className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center mb-12">
                <h1 className="text-3xl font-bold tracking-tight mb-4 md:mb-0">Your Dashboard</h1>

                {spotifyConnected ? (
                    <button
                        onClick={handleSync}
                        disabled={syncing}
                        className="bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 disabled:opacity-50"
                    >
                        <RefreshCw size={18} className={syncing ? "animate-spin text-orange-400" : "text-zinc-400"} />
                        <span>{syncing ? "Syncing APIs..." : "Sync Fresh Data"}</span>
                    </button>
                ) : (
                    <button
                        onClick={handleSpotifyLogin}
                        className="bg-[#1DB954] hover:bg-[#1ed760] text-white font-semibold py-2 px-6 rounded-full transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg shadow-green-500/20"
                    >
                        <span>Connect Spotify</span>
                    </button>
                )}
            </header>

            <main className="max-w-5xl mx-auto">
                {!spotifyConnected ? (
                    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-10 text-center flex flex-col items-center">
                        <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center mb-4">
                            <Music className="text-[#1DB954]" size={32} />
                        </div>
                        <h2 className="text-xl font-semibold mb-2">Spotify Connection Required</h2>
                        <p className="text-zinc-400 max-w-md">
                            Runify has linked your Strava account. To process your musical rhythms, you must connect your Spotify account.
                        </p>
                    </div>
                ) : loading ? (
                    <div className="flex justify-center items-center h-64">
                        <RefreshCw className="animate-spin text-zinc-600 w-8 h-8" />
                    </div>
                ) : runs.length === 0 ? (
                    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-10 text-center">
                        <p className="text-zinc-400">No runs synced yet. Go on a run, listen to music, and click "Sync Fresh Data".</p>
                    </div>
                ) : (
                    <div className="space-y-8">
                        {runs.map((run) => (
                            <div key={run.id} className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden hover:border-zinc-700 transition-colors">

                                {/* Run Header */}
                                <div className="p-6 border-b border-zinc-800/80 bg-zinc-900/50 flex flex-col md:flex-row justify-between items-start md:items-center">
                                    <div>
                                        <h3 className="text-xl font-bold text-white mb-2">{run.name}</h3>
                                        <div className="flex items-center space-x-4 text-sm text-zinc-400">
                                            <span className="flex items-center"><Calendar size={14} className="mr-1 inline" /> {format(new Date(run.start_date), 'MMM d, yyyy • h:mm a')}</span>
                                            <span className="flex items-center"><Activity size={14} className="mr-1 inline" /> {(run.distance_meters / 1000).toFixed(2)} km</span>
                                            <span>{Math.floor(run.elapsed_time_seconds / 60)} mins</span>
                                        </div>
                                    </div>

                                    <div className="mt-4 md:mt-0 bg-zinc-950 px-4 py-2 rounded-lg border border-zinc-800 flex items-center text-xs text-zinc-400 font-mono">
                                        <Music size={14} className="mr-2 text-green-400" />
                                        {run.tracks.length} tracks matched
                                    </div>
                                </div>

                                {/* Track List */}
                                <div className="p-6">
                                    {run.tracks.length > 0 ? (
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                            {run.tracks.map((track, i) => (
                                                <a
                                                    key={i}
                                                    href={track.external_url}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    className="flex items-center space-x-3 p-3 rounded-xl hover:bg-zinc-800 transition-colors group cursor-pointer"
                                                >
                                                    <img
                                                        src={track.album_image_url || 'https://via.placeholder.com/48'}
                                                        alt="album cover"
                                                        className="w-12 h-12 rounded object-cover shadow-sm group-hover:shadow-md"
                                                    />
                                                    <div className="flex-1 min-w-0">
                                                        <p className="text-sm font-medium text-white truncate">{track.name}</p>
                                                        <p className="text-xs text-zinc-400 truncate">{track.artist}</p>
                                                    </div>
                                                </a>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-zinc-500 py-4 text-center">No music history found playing during these timestamps.</p>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
};

export default Dashboard;
