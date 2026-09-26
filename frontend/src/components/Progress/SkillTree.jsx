import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Lock, BookOpen, Star, AlertCircle } from 'lucide-react';
import Card from '../Common/Card';

const SkillTree = ({ course }) => {
  if (!course || !course.topics) return null;

  return (
    <Card>
      <div className="p-8 relative overflow-hidden">
        <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">
          {course.name} Skill Tree
        </h2>

        <div className="relative flex flex-col items-center max-w-lg mx-auto">
          {/* SVG Connecting Line */}
          <div className="absolute top-0 bottom-0 left-1/2 w-1 bg-gray-200 transform -translate-x-1/2 z-0" />
          
          {course.topics.map((topic, index) => {
            // Determine side for zigzag layout
            const isLeft = index % 2 === 0;
            
            // Aggregate topic progress from subtopics
            const totalSubtopics = topic.subtopics.length;
            const unlockedSubtopics = topic.subtopics.filter(st => st.is_unlocked).length;
            const completedSubtopics = topic.subtopics.filter(st => st.is_completed).length;
            
            let state = 'locked';
            if (completedSubtopics === totalSubtopics && totalSubtopics > 0) {
              state = 'completed';
            } else if (unlockedSubtopics > 0) {
              state = 'in-progress';
            }
            
            // Calculate average knowledge if any subtopics exist
            const avgKnowledge = totalSubtopics > 0 
              ? topic.subtopics.reduce((acc, st) => acc + (st.knowledge_level || 0), 0) / totalSubtopics 
              : 0;

            return (
              <div 
                key={topic.id} 
                className={`relative z-10 w-full flex items-center justify-between mb-16 ${
                  isLeft ? 'flex-row' : 'flex-row-reverse'
                }`}
              >
                {/* Empty Spacer */}
                <div className="w-5/12"></div>

                {/* The Node */}
                <div className="w-2/12 flex justify-center relative">
                  {/* The connector to the side card */}
                  <div className={`absolute top-1/2 w-1/2 h-1 ${
                    state === 'locked' ? 'bg-gray-200' : 'bg-blue-400'
                  } ${isLeft ? 'left-full' : 'right-full'}`} />
                  
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    className={`w-16 h-16 rounded-full border-4 flex items-center justify-center bg-white z-20 shadow-lg ${
                      state === 'completed' 
                        ? 'border-green-500 text-green-500' 
                        : state === 'in-progress'
                        ? 'border-blue-500 text-blue-500'
                        : 'border-gray-300 text-gray-400'
                    }`}
                  >
                    {state === 'completed' ? (
                      <Star className="w-8 h-8 fill-current" />
                    ) : state === 'in-progress' ? (
                      <BookOpen className="w-8 h-8" />
                    ) : (
                      <Lock className="w-8 h-8" />
                    )}
                  </motion.div>
                </div>

                {/* Info Card */}
                <div className={`w-5/12 ${
                  isLeft ? 'pl-4 text-left' : 'pr-4 text-right'
                }`}>
                  <motion.div 
                    initial={{ opacity: 0, x: isLeft ? -20 : 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`p-4 rounded-xl shadow-sm border-2 ${
                      state === 'completed'
                        ? 'bg-green-50 border-green-200'
                        : state === 'in-progress'
                        ? 'bg-blue-50 border-blue-200'
                        : 'bg-gray-50 border-gray-200 opacity-75'
                    }`}
                  >
                    <h3 className={`font-bold text-lg mb-1 ${
                      state === 'locked' ? 'text-gray-500' : 'text-gray-800'
                    }`}>
                      {topic.name}
                    </h3>
                    <p className="text-xs text-gray-500 mb-2">
                      {completedSubtopics} / {totalSubtopics} Lessons
                    </p>
                    {state !== 'locked' && (
                      <div className="flex items-center gap-2">
                        <div className="h-2 flex-grow bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${
                              state === 'completed' ? 'bg-green-500' : 'bg-blue-500'
                            }`}
                            style={{ width: `${Math.round(avgKnowledge * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-gray-700">
                          {Math.round(avgKnowledge * 100)}%
                        </span>
                      </div>
                    )}
                  </motion.div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};

export default SkillTree;
