import "./App.css";

function App() {
  return (
    <div className="main_page">
      {/* Left Pane */}
      <div className="left_pane">
        <h3>History</h3>
        <p>Question 1</p>
        <p>Question 2</p>
        <p>Question 3</p>
        {/* Add more to see scrolling */}
      </div>

      {/* Right Pane */}
      <div className="right_pane">
        <div className="content_area">
          <h2>Results</h2>
          <p></p>
          {/* Add long content here to test scrolling */}
        </div>

        <input
          type="text"
          className="question_box"
          placeholder="Enter your question..."
        />
      </div>
    </div>
  );
}

export default App;
