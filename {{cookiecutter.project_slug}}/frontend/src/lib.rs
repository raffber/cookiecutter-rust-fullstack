mod utils;
mod controller;
mod view;

#[macro_use]
extern crate seed;
use wasm_bindgen::prelude::*;

use controller::update;
use view::view;

pub struct Model {
    dummy: String
}

impl Default for Model {
    fn default() -> Self {
        Model { 
            dummy: "Hello, World".to_string()
        }
    }
}

#[derive(Clone, Debug)]
pub enum Msg {
    Dummy
}


#[wasm_bindgen]
pub fn render() {
    utils::set_panic_hook();
    let state = seed::App::build(Model::default(), update, view)
        .finish()
        .run();
}