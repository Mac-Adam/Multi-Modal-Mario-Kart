// Copyright Epic Games, Inc. All Rights Reserved.

#include "Unreal_projectPawn.h"
#include "Unreal_projectWheelFront.h"
#include "Unreal_projectWheelRear.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Unreal_project.h"
#include "TimerManager.h"

#define LOCTEXT_NAMESPACE "VehiclePawn"

AUnreal_projectPawn::AUnreal_projectPawn()
{
	// construct the front camera boom
	FrontSpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("Front Spring Arm"));
	FrontSpringArm->SetupAttachment(GetMesh());
	FrontSpringArm->TargetArmLength = 0.0f;
	FrontSpringArm->bDoCollisionTest = false;
	FrontSpringArm->bEnableCameraRotationLag = true;
	FrontSpringArm->CameraRotationLagSpeed = 15.0f;
	FrontSpringArm->SetRelativeLocation(FVector(30.0f, 0.0f, 120.0f));

	FrontCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("Front Camera"));
	FrontCamera->SetupAttachment(FrontSpringArm);
	FrontCamera->bAutoActivate = false;

	// construct the back camera boom
	BackSpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("Back Spring Arm"));
	BackSpringArm->SetupAttachment(GetMesh());
	BackSpringArm->TargetArmLength = 650.0f;
	BackSpringArm->SocketOffset.Z = 150.0f;
	BackSpringArm->bDoCollisionTest = false;
	BackSpringArm->bInheritPitch = false;
	BackSpringArm->bInheritRoll = false;
	BackSpringArm->bEnableCameraRotationLag = true;
	BackSpringArm->CameraRotationLagSpeed = 2.0f;
	BackSpringArm->CameraLagMaxDistance = 50.0f;

	BackCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("Back Camera"));
	BackCamera->SetupAttachment(BackSpringArm);

	// Configure the car mesh
	GetMesh()->SetSimulatePhysics(true);
	GetMesh()->SetCollisionProfileName(FName("Vehicle"));

	// get the Chaos Wheeled movement component
	ChaosVehicleMovement = CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());

}

void AUnreal_projectPawn::SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		// // steering 
		// EnhancedInputComponent->BindAction(SteeringAction, ETriggerEvent::Triggered, this, &AUnreal_projectPawn::Steering);
		// EnhancedInputComponent->BindAction(SteeringAction, ETriggerEvent::Completed, this, &AUnreal_projectPawn::Steering);

		// // throttle 
		// EnhancedInputComponent->BindAction(ThrottleAction, ETriggerEvent::Triggered, this, &AUnreal_projectPawn::Throttle);
		// EnhancedInputComponent->BindAction(ThrottleAction, ETriggerEvent::Completed, this, &AUnreal_projectPawn::Throttle);

		// // break 
		// EnhancedInputComponent->BindAction(BrakeAction, ETriggerEvent::Triggered, this, &AUnreal_projectPawn::Brake);
		// EnhancedInputComponent->BindAction(BrakeAction, ETriggerEvent::Started, this, &AUnreal_projectPawn::StartBrake);
		// EnhancedInputComponent->BindAction(BrakeAction, ETriggerEvent::Completed, this, &AUnreal_projectPawn::StopBrake);

		// // handbrake 
		// EnhancedInputComponent->BindAction(HandbrakeAction, ETriggerEvent::Started, this, &AUnreal_projectPawn::StartHandbrake);
		// EnhancedInputComponent->BindAction(HandbrakeAction, ETriggerEvent::Completed, this, &AUnreal_projectPawn::StopHandbrake);

		// // look around 
		// EnhancedInputComponent->BindAction(LookAroundAction, ETriggerEvent::Triggered, this, &AUnreal_projectPawn::LookAround);

		// // toggle camera 
		// EnhancedInputComponent->BindAction(ToggleCameraAction, ETriggerEvent::Triggered, this, &AUnreal_projectPawn::ToggleCamera);

		// // reset the vehicle 
		// EnhancedInputComponent->BindAction(ResetVehicleAction, ETriggerEvent::Triggered, this, &AUnreal_projectPawn::ResetVehicle);
	}
	else
	{
		UE_LOG(LogUnreal_project, Error, TEXT("'%s' Failed to find an Enhanced Input component! This template is built to use the Enhanced Input system. If you intend to use the legacy system, then you will need to update this C++ file."), *GetNameSafe(this));
	}
}

void AUnreal_projectPawn::BeginPlay()
{
	Super::BeginPlay();

    FIPv4Endpoint Endpoint(FIPv4Address::Any, UDPPort);

    // 2. Create the Socket
    ListenSocket = FUdpSocketBuilder(TEXT("PythonControlSocket"))
        .AsNonBlocking()
        .AsReusable()
        .BoundToEndpoint(Endpoint)
        .WithReceiveBufferSize(1024);

    // 3. Create the Receiver and bind it to our function
    if (ListenSocket)
    {
        UE_LOG(LogTemp, Warning, TEXT("Successfully listening on Port %d"), UDPPort);
    }

	// set up the flipped check timer
	GetWorld()->GetTimerManager().SetTimer(FlipCheckTimer, this, &AUnreal_projectPawn::FlippedCheck, FlipCheckTime, true);
}

void AUnreal_projectPawn::EndPlay(EEndPlayReason::Type EndPlayReason)
{
	// clear the flipped check timer
	GetWorld()->GetTimerManager().ClearTimer(FlipCheckTimer);

	Super::EndPlay(EndPlayReason);

	if (ListenSocket) {
        ListenSocket->Close();
        ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(ListenSocket);
        ListenSocket = nullptr;
    }
}
void AUnreal_projectPawn::Tick(float Delta)
{
    Super::Tick(Delta);

    // add some angular damping if the vehicle is in midair
    bool bMovingOnGround = ChaosVehicleMovement->IsMovingOnGround();
    GetMesh()->SetAngularDamping(bMovingOnGround ? 0.0f : 3.0f);

    // realign the camera yaw to face front
    float CameraYaw = BackSpringArm->GetRelativeRotation().Yaw;
    CameraYaw = FMath::FInterpTo(CameraYaw, 0.0f, Delta, 1.0f);

    BackSpringArm->SetRelativeRotation(FRotator(0.0f, CameraYaw, 0.0f));

    // 1. Increment our safety timer every frame
    TimeSinceLastNetworkInput += Delta;

    if (ListenSocket)
    {
        uint32 Size;
        // While there is data waiting to be read...
        while (ListenSocket->HasPendingData(Size))
        {
            TArray<uint8> ReceivedData;
            ReceivedData.Init(0, FMath::Min(Size, 65507u)); // Max UDP payload

            int32 BytesRead = 0;
            TSharedRef<FInternetAddr> Sender = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->CreateInternetAddr();

            // Read the data!
            if (ListenSocket->RecvFrom(ReceivedData.GetData(), ReceivedData.Num(), BytesRead, *Sender))
            {
                ReceivedData.Add(0); // Null terminator
                FString ReceivedString = UTF8_TO_TCHAR(ReceivedData.GetData());
                
                // 2. We successfully received data! Reset the safety timer.
                TimeSinceLastNetworkInput = 0.0f;
                bIsNetworkTimeout = false; 

                FString Command;
                FString ValueString;
                
                if (ReceivedString.Split(TEXT(":"), &Command, &ValueString))
                {
                    float InputValue = FCString::Atof(*ValueString);
					UE_LOG(LogTemp, Warning, TEXT("Received Command: %s with Value: %f"), *Command, InputValue);
                    if (Command == TEXT("STEER"))
                    {
                        DoSteering(InputValue);
                    }
                    else if (Command == TEXT("THROTTLE"))
                    {
                        if (InputValue > 0.0f)
                        {
                            DoThrottle(InputValue);
                        }
                        else if (InputValue < 0.0f)
                        {
                            DoBrake(FMath::Abs(InputValue));
                        }
                        else
                        {
                            DoThrottle(0.0f);
                            DoBrake(0.0f);
                        }
                    }
                    else if (Command == TEXT("HANDBRAKE"))
                    {
                        if (InputValue > 0.0f) {
                            DoHandbrakeStart();
                        } else {
                            DoHandbrakeStop();
                        }
                    }
					else if (Command == TEXT("coffee"))
					{
						AudioCoffeDetected();
					}
					else if (Command == TEXT("chair"))	
					{
						AudioChairDetected();
					}
				}
            }
        }
    }

    // 3. The Dead Man's Switch (Timeout Logic)
    // If we haven't received data in 1 second, zero out all inputs.
    if (TimeSinceLastNetworkInput > 1.0f && !bIsNetworkTimeout)
    {
        UE_LOG(LogTemp, Warning, TEXT("Network connection dropped! Engaging safety brakes."));
        
        DoSteering(0.0f);
        DoThrottle(0.0f);
        DoBrake(0.0f);
        DoHandbrakeStop();

        // Set this to true so we don't spam the console and functions every single frame
        bIsNetworkTimeout = true; 
    }
}
void AUnreal_projectPawn::Steering(const FInputActionValue& Value)
{
	// route the input
	DoSteering(Value.Get<float>());
}

void AUnreal_projectPawn::Throttle(const FInputActionValue& Value)
{
	// route the input
	DoThrottle(Value.Get<float>());
}

void AUnreal_projectPawn::Brake(const FInputActionValue& Value)
{
	// route the input
	DoBrake(Value.Get<float>());
}

void AUnreal_projectPawn::StartBrake(const FInputActionValue& Value)
{
	// route the input
	DoBrakeStart();
}

void AUnreal_projectPawn::StopBrake(const FInputActionValue& Value)
{
	// route the input
	DoBrakeStop();
}

void AUnreal_projectPawn::StartHandbrake(const FInputActionValue& Value)
{
	// route the input
	DoHandbrakeStart();
}

void AUnreal_projectPawn::StopHandbrake(const FInputActionValue& Value)
{
	// route the input
	DoHandbrakeStop();
}

void AUnreal_projectPawn::LookAround(const FInputActionValue& Value)
{
	// route the input
	DoLookAround(Value.Get<float>());
}

void AUnreal_projectPawn::ToggleCamera(const FInputActionValue& Value)
{
	// route the input
	DoToggleCamera();
}

void AUnreal_projectPawn::ResetVehicle(const FInputActionValue& Value)
{
	// route the input
	DoResetVehicle();
}

void AUnreal_projectPawn::DoSteering(float SteeringValue)
{
	if (!bCanDrive) return;
	// add the input
	ChaosVehicleMovement->SetSteeringInput(SteeringValue);
}

void AUnreal_projectPawn::DoThrottle(float ThrottleValue)
{
	if (!bCanDrive) return;
	// add the input
	ChaosVehicleMovement->SetThrottleInput(ThrottleValue);

	// reset the brake input
	ChaosVehicleMovement->SetBrakeInput(0.0f);
}

void AUnreal_projectPawn::DoBrake(float BrakeValue)
{
	if (!bCanDrive) return;
	// add the input
	ChaosVehicleMovement->SetBrakeInput(BrakeValue);

	// reset the throttle input
	ChaosVehicleMovement->SetThrottleInput(0.0f);
}

void AUnreal_projectPawn::DoBrakeStart()
{
	if (!bCanDrive) return;
	// call the Blueprint hook for the brake lights
	BrakeLights(true);
}

void AUnreal_projectPawn::DoBrakeStop()
{
	if (!bCanDrive) return;
	// call the Blueprint hook for the brake lights
	BrakeLights(false);

	// reset brake input to zero
	ChaosVehicleMovement->SetBrakeInput(0.0f);
}

void AUnreal_projectPawn::DoHandbrakeStart()
{
	if (!bCanDrive) return;
	// add the input
	ChaosVehicleMovement->SetHandbrakeInput(true);

	// call the Blueprint hook for the break lights
	BrakeLights(true);
}

void AUnreal_projectPawn::DoHandbrakeStop()
{
	if (!bCanDrive) return;
	// add the input
	ChaosVehicleMovement->SetHandbrakeInput(false);

	// call the Blueprint hook for the break lights
	BrakeLights(false);
}

void AUnreal_projectPawn::DoLookAround(float YawDelta)
{
	if (!bCanDrive) return;
	// rotate the spring arm
	BackSpringArm->AddLocalRotation(FRotator(0.0f, YawDelta, 0.0f));
}

void AUnreal_projectPawn::DoToggleCamera()
{
	if (!bCanDrive) return;
	// toggle the active camera flag
	bFrontCameraActive = !bFrontCameraActive;

	FrontCamera->SetActive(bFrontCameraActive);
	BackCamera->SetActive(!bFrontCameraActive);
}

void AUnreal_projectPawn::DoResetVehicle()
{
	// reset to a location slightly above our current one
	FVector ResetLocation = GetActorLocation() + FVector(0.0f, 0.0f, 50.0f);

	// reset to our yaw. Ignore pitch and roll
	FRotator ResetRotation = GetActorRotation();
	ResetRotation.Pitch = 0.0f;
	ResetRotation.Roll = 0.0f;

	// teleport the actor to the reset spot and reset physics
	SetActorTransform(FTransform(ResetRotation, ResetLocation, FVector::OneVector), false, nullptr, ETeleportType::TeleportPhysics);

	GetMesh()->SetPhysicsAngularVelocityInDegrees(FVector::ZeroVector);
	GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);
}

void AUnreal_projectPawn::FlippedCheck()
{
	// check the difference in angle between the mesh's up vector and world up
	const float UpDot = FVector::DotProduct(FVector::UpVector, GetMesh()->GetUpVector());

	if (UpDot < FlipCheckMinDot)
	{
		// is this the second time we've checked that the vehicle is still flipped?
		if (bPreviousFlipCheck)
		{
			// reset the vehicle to upright
			DoResetVehicle();
		}
		
		// set the flipped check flag so the next check resets the car
		bPreviousFlipCheck = true;

	} else {

		// we're upright. reset the flipped check flag
		bPreviousFlipCheck = false;
	}
}

#undef LOCTEXT_NAMESPACE