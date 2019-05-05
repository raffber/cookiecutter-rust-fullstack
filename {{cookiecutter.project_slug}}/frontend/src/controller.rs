use seed::prelude::*;

pub fn update(msg: Msg, model: &mut Model) -> Update<Msg> {
    log!(format!("{:?}", msg));
    match msg {
        Msg::Dummy => Render.into()
    }
}
