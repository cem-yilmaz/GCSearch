import React from "react";

import "./PlatformSelector.css";

const PlatformSelector = ({ onPlatformSelected, selectedPlatform }) => {
    return (
        <div className="platform-selector">
            <div className={`instagram ${selectedPlatform === "instagram" ? "selected" : ""}`} onClick={() => onPlatformSelected("instagram")}>
                <img src="/assets/platform_logos/instagram.png" alt="Instagram" />
            </div>
            <div className={`whatsapp ${selectedPlatform === "whatsapp" ? "selected" : ""}`} onClick={() => onPlatformSelected("whatsapp")}>
                <img src="/assets/platform_logos/whatsapp.png" alt="WhatsApp" />
            </div>
            <div className={`wechat ${selectedPlatform === "wechat" ? "selected" : ""}`} onClick={() => onPlatformSelected("wechat")}>
                <img src="/assets/platform_logos/wechat.png" alt="WeChat" />
            </div>
            <div className={`line ${selectedPlatform === "line" ? "selected" : ""}`} onClick={() => onPlatformSelected("line")}>
                <img src="/assets/platform_logos/line.png" alt="LINE" />
            </div>
        </div>
    )
};

export default PlatformSelector;