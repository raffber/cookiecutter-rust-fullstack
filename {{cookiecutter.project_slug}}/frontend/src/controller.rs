use seed::prelude::*;
use super::{Msg, Model};


pub fn update(msg: Msg, model: &mut Model) -> Update<Msg> {
    log!(format!("{:?}", msg));
    match msg {
        Msg::Dummy => Render.into()
    }
}
