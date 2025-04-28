import React from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../hooks/authContext';
import { UserIcon, HomeIcon, ChartBarIcon, ClockIcon } from '@heroicons/react/24/outline';

interface DashboardProps {
  isDarkMode: boolean;
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ isDarkMode, onLogout }) => {
  const { accessToken } = useAuth();

  return (
    <div className={`p-6 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
      {/* Header section */}
      <div className="relative h-20 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-lg mb-6 flex items-center px-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center"
        >
          <div className="mr-4 bg-white/20 p-2 rounded-full">
            <UserIcon className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Welcome to DreamApp</h1>
            <p className="text-sm text-white/80">Your personal dashboard</p>
          </div>
        </motion.div>
      </div>

      {/* Main content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
      >
        <div className={`p-5 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'} shadow-md mb-6`}>
          <div className="flex items-center border-b border-gray-200 dark:border-gray-700 pb-4 mb-4">
            <div className="bg-indigo-100 dark:bg-indigo-900 p-2 rounded-lg mr-3">
              <HomeIcon className="h-5 w-5 text-indigo-600 dark:text-indigo-300" />
            </div>
            <h2 className="text-xl font-semibold">Welcome, User!</h2>
          </div>
          <p className={`${isDarkMode ? 'text-gray-300' : 'text-gray-600'} mb-3`}>
            This is a basic landing page. More features will be added in future development phases.
          </p>
          <div className="flex space-x-2 items-center mt-4 py-2 px-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
            <div className={`w-3 h-3 rounded-full bg-green-500 animate-pulse`}></div>
            <span className={`text-sm ${isDarkMode ? 'text-green-300' : 'text-green-700'}`}>Authentication status: Active</span>
          </div>
        </div>
      </motion.div>

      {/* Dashboard widgets */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'} shadow-md`}
          whileHover={{ y: -5, transition: { duration: 0.2 } }}
        >
          <div className="flex items-center mb-3">
            <div className={`p-2 rounded-md ${isDarkMode ? 'bg-blue-900/30' : 'bg-blue-100'} mr-3`}>
              <ChartBarIcon className={`h-5 w-5 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
            </div>
            <h3 className="text-lg font-semibold">Quick Stats</h3>
          </div>
          <div className={`py-8 flex items-center justify-center ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} border border-dashed rounded-lg`}>
            <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-500'} text-center`}>Coming soon...</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'} shadow-md`}
          whileHover={{ y: -5, transition: { duration: 0.2 } }}
        >
          <div className="flex items-center mb-3">
            <div className={`p-2 rounded-md ${isDarkMode ? 'bg-purple-900/30' : 'bg-purple-100'} mr-3`}>
              <ClockIcon className={`h-5 w-5 ${isDarkMode ? 'text-purple-400' : 'text-purple-600'}`} />
            </div>
            <h3 className="text-lg font-semibold">Recent Activity</h3>
          </div>
          <div className={`py-8 flex items-center justify-center ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} border border-dashed rounded-lg`}>
            <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-500'} text-center`}>Coming soon...</p>
          </div>
        </motion.div>
      </div>

      {/* Logout button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onLogout}
        className={`px-4 py-2 rounded-lg ${
          isDarkMode 
            ? 'bg-red-600 hover:bg-red-700' 
            : 'bg-red-500 hover:bg-red-600'
        } text-white transition-colors`}
      >
        Logout
      </motion.button>
    </div>
  );
};

export default Dashboard;