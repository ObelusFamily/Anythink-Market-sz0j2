import React from "react";
import agent from "../../agent";
import logo from "../../imgs/logo.png";

const SearchBox = (props) => {
  const changeHandler = (ev) => {
    ev.preventDefault();
    if (ev.target.value.length >= 3) {
      props.onSearchChanged(
        ev.target.value,
        (page) => agent.Items.byTitle(ev.target.value, page),
        agent.Items.byTitle(ev.target.value)
      );
    } else {
      props.onSearchChanged(
        "",
        (page) => agent.Items.byTitle("", page),
        agent.Items.byTitle("")
      );
    }
  };
  return (
    <input
      id="search-box"
      placeholder="what is it that you trully desire?"
      onChange={changeHandler}
    ></input>
  );
};

const Banner = (props) => {
  return (
    <div className="banner text-white">
      <div className="container p-4 text-center">
        <img src={logo} alt="banner" />
        <div>
          <span id="get-part">A place to get</span>
          <SearchBox onSearchChanged={props.onSearchChanged} />
          <span> the cool stuff.</span>
        </div>
      </div>
    </div>
  );
};

export default Banner;
