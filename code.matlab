

% Extract patient list
Process_Folder='C:\Users\prock\Desktop\Radiology\Research\CTDenoise'
cd(Process_Folder);


list=dir('.\2020*');  % Get list of cases
spm_jobman('initcfg');


ct_fname='D:\CTDenoise_200\dummy.nii';bw

for i=1:length(list),

    current=pwd;

    cd(list(i).name);

    % Find Axial series
    series_names=dir('*BRAIN*');
    if length(series_names)==0, series_names=dir('*head*');end
    if length(series_names)==0, series_names=dir('*AXIAL*');end
    exclude=[];
    if length(series_names)>=1,
        for k=1:length(series_names),
            if (length(findstr(series_names(k).name,'SAGITTAL'))>0 | length(findstr(series_names(k).name,'CORONAL'))>0 | length(findstr(upper(series_names(k).name),'TRUE'))>0),
                exclude=[exclude k];
            end
        end
    end
    series_names(exclude)=[];
    if length(series_names)>1,
        disp(sprintf('%0d: %s',i,list(i).name));
    end

    if length(series_names)==0,
        disp([list(i).name ' no match']);
    else
        disp([list(i).name '\' series_names.name]);


        cd(series_names(1).name);
        files=dir('CT*'); % Get list of DICOM files that are in the Axial series
        InstanceNumber=zeros(1,length(files));
        ct=zeros(512,512,length(files));
        % Get the image content and sort in the proper order and put it in ct (x,y,z)
        for f=1:length(files),
            obj = images.internal.dicom.DICOMFile(files(f).name);
            InstanceNumber(f)= obj.getAttributeByName('InstanceNumber');
            ct(:,:,InstanceNumber(f))=dicomread(files(f).name)*obj.getAttributeByName('RescaleSlope')+obj.getAttributeByName('RescaleIntercept');
        end


        % CT Preprocessing 1 (set the intensity mode to 37 HU)
        ct_mode=mode(ct(ct<77 & ct>10));
        ct=ct-ct_mode+37;
        ind=ct<77 & ct>0;
 

        % Identify non-brain tissues in a mask for removal in three different orientations
        bone=ind==1;
        % Sag Skull Bottom and Top Detection second pass
        for k=1:size(bone,1),
            CC=bwconncomp(squeeze(bone(k,:,:)));
            numPixels = cellfun(@numel,CC.PixelIdxList);
            [biggest,idx] = sort(numPixels,'descend');
            if length(idx)>0,
                mask=zeros(size(squeeze(bone(k,:,:))));
                mask(CC.PixelIdxList{idx(1)}) = 1;
                bone(k,:,:)=mask;
            end
        end
        CC=bwconncomp(bone);
        numPixels = cellfun(@numel,CC.PixelIdxList);
        [biggest,idx] = max(numPixels);
        bone=ones(size(ind));
        bone(CC.PixelIdxList{idx}) = 0;
        se = strel('disk',3); 
        bone=imerode(bone,se);
        bone_sag=bone;

 
        bone=ind==1;
        % Skull Bottom and Top Detection second pass
        for k=1:size(bone,3),
            CC=bwconncomp(squeeze(bone(:,:,k)));
            numPixels = cellfun(@numel,CC.PixelIdxList);
            [biggest,idx] = sort(numPixels,'descend');
            if length(idx)>0,
                mask=zeros(size(squeeze(bone(:,:,k))));
                mask(CC.PixelIdxList{idx(1)}) = 1;
                bone(:,:,k)=mask;
            end
        end
        CC=bwconncomp(bone);
        numPixels = cellfun(@numel,CC.PixelIdxList);
        [biggest,idx] = max(numPixels);
        bone=ones(size(ind));
        bone(CC.PixelIdxList{idx}) = 0;
        se = strel('disk',3); 
        bone=imerode(bone,se);
        bone_ax=bone;


        bone=ind==1;
        % Skull Bottom and Top Detection
        for k=1:size(bone,2),
            CC=bwconncomp(squeeze(bone(:,k,:)));
            numPixels = cellfun(@numel,CC.PixelIdxList);
            [biggest,idx] = sort(numPixels,'descend');
            if length(idx)>0,
                mask=zeros(size(squeeze(bone(:,k,:))));
                mask(CC.PixelIdxList{idx(1)}) = 1;
                bone(:,k,:)=mask;
            end
        end
        CC=bwconncomp(bone);
        numPixels = cellfun(@numel,CC.PixelIdxList);
        [biggest,idx] = max(numPixels);
        bone=ones(size(ind));
        bone(CC.PixelIdxList{idx}) = 0;
        se = strel('disk',3); 
        bone=imerode(bone,se);
        bone_cor=bone;


        ind=~((bone_cor+bone_ax+bone_sag)<=1);

 
        % Skull Bottom and Top Detection
        holes=squeeze(sum(sum(~ind,1),2));
        peakarea=max(holes);
        peakloc=find(holes==peakarea);
        peakloc=peakloc(1);
        top=max(find(holes(floor(size(bone,3)*.66):size(bone,3))>peakarea*.02));
        top=floor(size(bone,3)*.66)+top(1)-1;
        holes=holes(1:peakloc);
        bottom=min(find(holes>peakarea*.02));


        if (top+1)<=size(bone,3),
            ind(:,:,(top+1):end)=1;
        end
        if (bottom-1)>=1,
            ind(:,:,1:(bottom-1))=1;
        end
 

        % Final cleanup
        se = strel('disk',3); 
        ind=imdilate(ind,se);
        CC=bwconncomp(~ind)
        numPixels = cellfun(@numel,CC.PixelIdxList);
        [biggest,idx] = max(numPixels);
        ind=ones(size(ind));
        ind(CC.PixelIdxList{idx}) = 0;
 

        ct=ct.*(ct>=0 & ct<=100);

        % Write skull-stripped CT to a NIFTI file
        cd('..');
        tmp=spm_vol(ct_fname);
        tmp.fname='CT_Ax.nii';
        tmp.dim=size(ct);
        tmp.dt=[spm_type('int16') 0];
        spm_write_vol(tmp,floor(ct.*~ind));
        gzip(tmp.fname);
        delete(tmp.fname);


    end
    cd(current);
end