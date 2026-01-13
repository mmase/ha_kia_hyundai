# Kia Connect (USA) - Community Maintained

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/MarcusTaz/ha_kia_hyundai.svg)](https://github.com/MarcusTaz/ha_kia_hyundai/releases)
[![License](https://img.shields.io/github/license/MarcusTaz/ha_kia_hyundai.svg)](LICENSE)

A Home Assistant integration for **Kia Connect (USA)** with **OTP authentication support**. This is a community-maintained fork that fixes critical issues after the original repository was archived.

## 🚗 What This Integration Does

Connect your USA Kia vehicle to Home Assistant and control:
- 🔋 Battery level & charging status
- 🌡️ Climate control (start/stop HVAC remotely)
- 🔒 Door locks (lock/unlock)
- 📍 Vehicle location
- ⚡ Charge limits (AC/DC)
- 🚪 Door, trunk, and hood status
- 🔧 Tire pressure warnings
- 📊 Odometer & range
- 🔌 Charging switch (start/stop charging when plugged in)

## ⚠️ Important Notes

- **USA ONLY** - This integration only works with Kia vehicles registered in the United States
- **OTP Support** - Fully supports the new OTP (One-Time Password) authentication via SMS or Email
- **Kia Connect Subscription Required** - Your vehicle must have an active Kia Connect subscription

## 🔧 Why This Fork Exists

The original [dahlb/ha_kia_hyundai](https://github.com/dahlb/ha_kia_hyundai) repository was **archived in December 2024** due to API challenges. However, the community still needs this integration!

**This fork provides:**
- ✅ **Fixed OTP authentication** (works with Kia's current API)
- ✅ **Bug fixes** for config flow errors
- ✅ **Active maintenance** for the community
- ✅ **Updated dependencies**

## 📦 Installation

### Via HACS (Recommended)

1. Open **HACS** in Home Assistant
2. Click the **three dots** (⋮) in the top right
3. Select **"Custom repositories"**
4. Add this repository URL: `https://github.com/MarcusTaz/ha_kia_hyundai`
5. Category: **Integration**
6. Click **"Add"**
7. Search for **"Kia Connect (USA)"** and install
8. **Restart Home Assistant**

### Manual Installation

1. Download the latest release
2. Extract to `/config/custom_components/ha_kia_hyundai/`
3. Restart Home Assistant

## ⚙️ Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Kia US"**
4. Enter your **Kia Connect username and password**
5. Choose **OTP delivery method** (SMS or Email)
6. Enter the **OTP code** when prompted
7. Your vehicle(s) will be automatically added!

### Multiple Vehicles

If you have multiple vehicles on your Kia account, they will all be added automatically in a single setup flow.

## 🔄 Update Frequency

- **Cached data fetch**: Every 10 minutes (configurable)
- **Force update**: Not recommended frequently to avoid draining 12V battery

## 🎛️ Services

### Climate Control
- `climate.set_temperature` - Set target temperature
- `climate.turn_on` - Start climate (uses preset defrost/heating settings)
- `climate.turn_off` - Stop climate

### Charging
- `switch.turn_on` / `switch.turn_off` - Start/stop charging (when plugged in)
- `number.set_value` - Set AC/DC charge limits

### Vehicle Actions
- `lock.lock` / `lock.unlock` - Lock/unlock doors
- `button.press` - Request vehicle status update (use sparingly!)

## 🐛 Troubleshooting

### OTP Issues
- Make sure you select the correct OTP method (SMS or Email)
- Check your phone/email for the code
- Code expires after a few minutes - request a new one if needed

### "Invalid handler specified" Error
This has been fixed in this fork! Make sure you're using the latest version.

### Authentication Failed
1. Verify your Kia Connect credentials work in the official app
2. Make sure your Kia Connect subscription is active
3. Enable debug logging (see below) and check logs

### Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.ha_kia_hyundai: debug
```

Then go to **Settings** → **System** → **Logs** and look for errors.

## 📝 Supported Entities

### Sensors
- Battery level (12V)
- EV battery level
- Charging status
- Plugged in status
- Odometer
- EV range
- Last update timestamp
- Tire pressure warnings
- Door/trunk/hood status
- Low fuel warning

### Controls
- Door locks
- Climate control
- Charging switch
- Charge limit numbers (AC/DC)
- Heated steering wheel
- Heated rear window
- Defrost/heating acc switches

### Buttons
- Force update (requests fresh data from vehicle)

## ⚖️ License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Credits

- **Original Author**: [Bren Dahl (@dahlb)](https://github.com/dahlb) - Thank you for creating this integration!
- **OTP Fix**: ❤️ mmase ❤️ - For the critical OTP authentication fix
- **Community Maintainer**: MarcusTaz - Keeping it alive for the community
- **API Library**: [kia-hyundai-api](https://github.com/dahlb/kia-hyundai-api)

## 🤝 Contributing

This is a community-maintained project! Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Disclaimer

This integration is not affiliated with, endorsed by, or connected to Kia Motors. Use at your own risk. Excessive API calls may drain your vehicle's 12V battery.

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/MarcusTaz/ha_kia_hyundai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MarcusTaz/ha_kia_hyundai/discussions)

---

**If this integration helps you, please ⭐ star the repo to show support!**
