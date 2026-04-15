// Copyright Epic Games, Inc. All Rights Reserved.

#include "Unreal_projectWheelRear.h"
#include "UObject/ConstructorHelpers.h"

UUnreal_projectWheelRear::UUnreal_projectWheelRear()
{
	AxleType = EAxleType::Rear;
	bAffectedByHandbrake = true;
	bAffectedByEngine = true;
}