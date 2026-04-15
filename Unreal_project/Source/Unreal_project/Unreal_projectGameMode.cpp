// Copyright Epic Games, Inc. All Rights Reserved.

#include "Unreal_projectGameMode.h"
#include "Unreal_projectPlayerController.h"

AUnreal_projectGameMode::AUnreal_projectGameMode()
{
	PlayerControllerClass = AUnreal_projectPlayerController::StaticClass();
}
