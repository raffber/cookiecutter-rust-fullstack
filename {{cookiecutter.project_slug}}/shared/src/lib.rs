use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicUsize, Ordering};


#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct TorrentLink {
    pub some_data: String,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Id {
    id: usize
}

static COUNTER: AtomicUsize = AtomicUsize::new(0);

impl Id {
    pub fn new() -> Id {
        let id = COUNTER.fetch_add(1, Ordering::SeqCst);
        Id { id }
    }
}
