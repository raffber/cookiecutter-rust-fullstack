use seed::prelude::*;
use super::{Msg, Model};


pub fn view(model: &Model) -> El<Msg> {
    div![ model.dummy ]
}