// components/JobCard.jsx
export function JobCard({ job, onApply }) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-xl font-bold text-gray-900">{job.title}</h2>
          <span className="px-3 py-1 bg-purple-100 text-[#c6269e] rounded-full text-sm">
            {job.matchScore}% Match
          </span>
        </div>
        <div className="mb-4">
          <p className="text-gray-600 font-medium mb-1">{job.company}</p>
          <p className="text-gray-500 text-sm mb-2">{job.location}</p>
          <p className="text-gray-700">{job.description}</p>
        </div>
        <div className="flex flex-wrap gap-2 mb-4">
          {job.skills?.map((skill) => (
            <span key={skill} className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded">
              {skill}
            </span>
          ))}
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">Posted {job.postedDate}</span>
          <button
            onClick={() => onApply(job.id)}
            className="px-4 py-2 bg-[#c6269e] text-white rounded hover:bg-[#a81f85] transition-colors"
          >
            Next Step
          </button>
        </div>
      </div>
    );
  }