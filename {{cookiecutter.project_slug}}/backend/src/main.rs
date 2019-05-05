#![feature(proc_macro_hygiene, decl_macro)]

#[macro_use] extern crate rocket;

use rocket_contrib::serve::StaticFiles;

use rocket::Rocket;
use rocket::response::Redirect;


#[get("/")]
fn home() -> Redirect {
    Redirect::to("/static/html/index.html")
}

fn get_assets_dir(rocket: &Rocket) -> String {
    rocket.config().get_str("assets_dir").unwrap().to_string().clone()
}

fn get_serve_static(rocket: &Rocket) -> bool {
    rocket.config().get_bool("serve_static").unwrap()
}

fn main() {
    let mut rocket = rocket::ignite();
    rocket = rocket.mount("/", routes![home]);
    let assets_dir = get_assets_dir(&rocket);
    let serve_static = get_serve_static(&rocket);
    if serve_static {
        rocket = rocket.mount("/static", StaticFiles::from(assets_dir));
    }
    rocket.launch();
}
