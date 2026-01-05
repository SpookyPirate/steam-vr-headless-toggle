// Simple Virtual Controller Driver for OpenVR
// Creates virtual VR controllers that appear in SteamVR

#include <openvr_driver.h>
#include <string>
#include <vector>
#include <fstream>

using namespace vr;

// Simple virtual controller device
class VirtualController : public ITrackedDeviceServerDriver
{
private:
    uint32_t m_unObjectId;
    PropertyContainerHandle_t m_ulPropertyContainer;
    std::string m_sSerialNumber;
    std::string m_sModelNumber;
    int m_nControllerIndex;
    ETrackedControllerRole m_nControllerRole;

public:
    VirtualController(int index, ETrackedControllerRole role)
        : m_unObjectId(k_unTrackedDeviceIndexInvalid)
        , m_ulPropertyContainer(k_ulInvalidPropertyContainer)
        , m_nControllerIndex(index)
        , m_nControllerRole(role)
    {
        m_sSerialNumber = "VIRTUAL_CTRL_" + std::to_string(index);
        m_sModelNumber = "VirtualController_v1";
    }

    virtual EVRInitError Activate(uint32_t unObjectId) override
    {
        m_unObjectId = unObjectId;
        m_ulPropertyContainer = VRProperties()->TrackedDeviceToPropertyContainer(m_unObjectId);

        // Set up properties
        VRProperties()->SetStringProperty(m_ulPropertyContainer, Prop_SerialNumber_String, m_sSerialNumber.c_str());
        VRProperties()->SetStringProperty(m_ulPropertyContainer, Prop_ModelNumber_String, m_sModelNumber.c_str());
        VRProperties()->SetStringProperty(m_ulPropertyContainer, Prop_ManufacturerName_String, "Virtual");
        VRProperties()->SetStringProperty(m_ulPropertyContainer, Prop_RenderModelName_String, "vr_controller_vive_1_5");

        VRProperties()->SetInt32Property(m_ulPropertyContainer, Prop_ControllerRoleHint_Int32, m_nControllerRole);
        VRProperties()->SetInt32Property(m_ulPropertyContainer, Prop_DeviceClass_Int32, TrackedDeviceClass_Controller);

        VRProperties()->SetBoolProperty(m_ulPropertyContainer, Prop_WillDriftInYaw_Bool, false);
        VRProperties()->SetBoolProperty(m_ulPropertyContainer, Prop_DeviceIsWireless_Bool, true);
        VRProperties()->SetBoolProperty(m_ulPropertyContainer, Prop_DeviceIsCharging_Bool, false);
        VRProperties()->SetFloatProperty(m_ulPropertyContainer, Prop_DeviceBatteryPercentage_Float, 1.0f);

        return VRInitError_None;
    }

    virtual void Deactivate() override
    {
        m_unObjectId = k_unTrackedDeviceIndexInvalid;
    }

    virtual void EnterStandby() override {}

    virtual void *GetComponent(const char *pchComponentNameAndVersion) override
    {
        return nullptr;
    }

    virtual void DebugRequest(const char *pchRequest, char *pchResponseBuffer, uint32_t unResponseBufferSize) override
    {
        if (unResponseBufferSize >= 1)
            pchResponseBuffer[0] = 0;
    }

    virtual DriverPose_t GetPose() override
    {
        DriverPose_t pose = { 0 };
        pose.poseIsValid = true;
        pose.result = TrackingResult_Running_OK;
        pose.deviceIsConnected = true;

        pose.qWorldFromDriverRotation.w = 1.0;
        pose.qWorldFromDriverRotation.x = 0.0;
        pose.qWorldFromDriverRotation.y = 0.0;
        pose.qWorldFromDriverRotation.z = 0.0;

        pose.qDriverFromHeadRotation.w = 1.0;
        pose.qDriverFromHeadRotation.x = 0.0;
        pose.qDriverFromHeadRotation.y = 0.0;
        pose.qDriverFromHeadRotation.z = 0.0;

        // Position controllers at a reasonable location
        pose.vecPosition[0] = (m_nControllerRole == TrackedControllerRole_LeftHand) ? -0.2 : 0.2;
        pose.vecPosition[1] = 1.0;
        pose.vecPosition[2] = -0.5;

        return pose;
    }
};

// Driver provider class
class VirtualControllerProvider : public IServerTrackedDeviceProvider
{
private:
    std::vector<VirtualController*> m_vecControllers;

public:
    virtual EVRInitError Init(IVRDriverContext *pDriverContext) override
    {
        VR_INIT_SERVER_DRIVER_CONTEXT(pDriverContext);

        // Read config to determine how many controllers to create
        EVRSettingsError error = VRSettingsError_None;
        int controllerCount = VRSettings()->GetInt32("driver_virtualcontroller", "controller_count", &error);
        if (error != VRSettingsError_None)
        {
            controllerCount = 2; // Default to 2 controllers if setting not found
        }

        // Create controllers
        for (int i = 0; i < controllerCount && i < 4; i++)
        {
            ETrackedControllerRole role = TrackedControllerRole_Invalid;
            if (i == 0) role = TrackedControllerRole_LeftHand;
            else if (i == 1) role = TrackedControllerRole_RightHand;

            VirtualController* pController = new VirtualController(i, role);
            m_vecControllers.push_back(pController);
            VRServerDriverHost()->TrackedDeviceAdded(("VIRTUAL_CTRL_" + std::to_string(i)).c_str(), TrackedDeviceClass_Controller, pController);
        }

        return VRInitError_None;
    }

    virtual void Cleanup() override
    {
        for (auto pController : m_vecControllers)
        {
            delete pController;
        }
        m_vecControllers.clear();
    }

    virtual const char * const *GetInterfaceVersions() override
    {
        return k_InterfaceVersions;
    }

    virtual void RunFrame() override {}

    virtual bool ShouldBlockStandbyMode() override
    {
        return false;
    }

    virtual void EnterStandby() override {}

    virtual void LeaveStandby() override {}
};

VirtualControllerProvider g_serverDriverProvider;

extern "C" __declspec(dllexport) void *HmdDriverFactory(const char *pInterfaceName, int *pReturnCode)
{
    if (0 == strcmp(IServerTrackedDeviceProvider_Version, pInterfaceName))
    {
        return &g_serverDriverProvider;
    }

    if (pReturnCode)
        *pReturnCode = VRInitError_Init_InterfaceNotFound;

    return nullptr;
}
