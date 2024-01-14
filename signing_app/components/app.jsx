import React from 'react';
import ReactDom from 'react-dom/client';

function App(props) {
  return (
    <h1>{props.title}</h1>
  )
}

const root = ReactDom.createRoot(document.getElementById("app"));
root.render(
  <App {...window.props} />
);