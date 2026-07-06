// components/ProfileCompletion.jsx
export function ProfileCompletion({ profile }) {
    const steps = [
      { key: 'resume', label: 'Upload Resume', completed: !!profile.resume },
      { key: 'github', label: 'Link GitHub', completed: !!profile.github },
      { key: 'leetcode', label: 'Link LeetCode', completed: !!profile.leetcode },
      // Skills step removed
    ];
  
    const completedSteps = steps.filter(step => step.completed).length;
    const completionPercentage = (completedSteps / steps.length) * 100;
  
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Profile Completion</h3>
        <div className="mb-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-[#c6269e] h-2 rounded-full transition-all duration-500"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {completionPercentage}% Complete
          </p>
        </div>
        <ul className="space-y-3">
          {steps.map((step) => (
            <li key={step.key} className="flex items-center">
              <span className={`w-4 h-4 rounded-full mr-3 ${
                step.completed ? 'bg-[#c6269e]' : 'bg-gray-200'
              }`} />
              <span className={step.completed ? 'text-gray-900' : 'text-gray-500'}>
                {step.label}
              </span>
            </li>
          ))}
        </ul>
      </div>
    );
  }