import React from "react";

import "./PlatformSelector.css";

const PlatformSelector = () => {
    return (
        <div className="platform-selector">
            <div className="instagram">
                <img src="/assets/platform_logos/instagram.png" alt="Instagram" />
            </div>
            <div className="whatsapp">
                <img src="/assets/platform_logos/whatsapp.png" alt="WhatsApp" />
            </div>
            <div className="wechat">
                <img src="/assets/platform_logos/wechat.png" alt="WeChat" />
            </div>
            <div className="line">
                <img src="/assets/platform_logos/line.png" alt="LINE" />
            </div>
        </div>
    )
};

export default PlatformSelector;