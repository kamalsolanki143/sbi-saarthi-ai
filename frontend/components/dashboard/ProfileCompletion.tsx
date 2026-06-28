'use client'

export default function ProfileCompletion() {
  const progress = 75

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">
        Profile Completion
      </h3>

      <p className="text-gray-600 mb-3">
        Your profile is {progress}% complete.
      </p>

      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className="bg-blue-600 h-3 rounded-full"
          style={{ width: `${progress}%` }}
        />
      </div>

      <button className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
        Complete Profile
      </button>
    </div>
  )
}