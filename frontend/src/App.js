import FacultyDashboard from "./FacultyDashboard";

function App() {
  return (
    <div className="w-full flex flex-col items-center mt-8">
      <h1 className="text-3xl font-bold mb-8"></h1>

      <div className="w-full max-w-4xl">
        <FacultyDashboard />
      </div>
    </div>
  );
}

export default App;
