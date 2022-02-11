import torch
import finetuner as ft
import torchvision
from docarray import DocumentArray
from finetuner.tuner.pytorch.losses import TripletLoss
from finetuner.tuner.pytorch.miner import TripletEasyHardMiner


def assign_label_and_preprocess(doc):
    doc.tags['finetuner_label'] = doc.uri.split('/')[2]
    return doc.load_uri_to_image_tensor()\
        .set_image_tensor_shape((224, 224))\
        .set_image_tensor_normalization()\
        .set_image_tensor_channel_axis(-1, 0)


def hit_rate(da, topk=1):
    hit = 0
    for d in da:
        for m in d.matches[:topk]:
            if d.uri.split('/')[-1] == m.uri.split('/')[-1]:
                hit += 1
    return hit / len(da)


if __name__ == "__main__":
    resnet = torchvision.models.resnet50(pretrained=False)
    resnet.load_state_dict(torch.load("data/checkpoint.pkt"), strict=False)

    ft.display(resnet, (3, 224, 224))

    train_da = DocumentArray.from_files("data/tiki/*/*.jpg")
    train_da.apply(assign_label_and_preprocess)

    print(f"There are {len(train_da)} samples in the training.")

    tuned_model = ft.fit(
        model=resnet,
        train_data=train_da,
        epochs=6,
        batch_size=128,
        loss=TripletLoss(miner=TripletEasyHardMiner(neg_strategy='hard'), margin=0.3),
        learning_rate=1e-5,
        device='cpu',
        to_embedding_model=True,
        input_size=(3, 224, 224),
        layer_name='adaptiveavgpool2d_173',
        num_items_per_class=3,
        freeze=['conv2d_1', 'batchnorm2d_2', 'conv2d_5', 'batchnorm2d_6', 'conv2d_8', 'batchnorm2d_9', 'conv2d_11', 'batchnorm2d_12'],
    )

    emb = train_da.embed(tuned_model, device="cpu")
    emb.match(train_da, limit=10)

    for k in range(1, 11):
        print(f'hit@{k}:  finetuned: {hit_rate(train_da, k):.3f}')

    torch.save(tuned_model.state_dict(), "../data/checkpoint.pkt")
