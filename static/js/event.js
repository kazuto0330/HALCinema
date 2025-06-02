document.addEventListener('DOMContentLoaded', () => {
    const EventUrl = document.getElementById("EventUrl");
    const EventUrlTxt = EventUrl.textContent;
    console.log(EventUrlTxt);
    if (EventUrlTxt == "None"){
        console.log("このイベントには外部のurlはありません。");
        EventUrl.style.display = "none";
    }
});